"""Wrapper classes for Blender native objects to facilitate conversion to
JME-usable format"""

__version__ = '$Revision$'
__date__ = '$Date$'
__author__ = 'Blaine Simpson, blaine (dot) simpson (at) admc (dot) com'
__url__ = 'http://www.jmonkeyengine.com'

# Copyright (c) 2009, Blaine Simpson and the jMonkeyEngine team
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Blaine Simpson and the jMonkeyEngine team
# ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Blaine Simpson or the jMonkeyEngine team
# BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from jme.xml import XmlTag as _XmlTag
import jme.esmath as _esmath
import Blender.Mathutils as _bmath
from Blender.Material import Modes as _matModes
from Blender.Mesh import Modes as _meshModes
from Blender import Armature as _Armature

# GENERAL DEVELOPMENT NOTES:
#
# For unsupported Blender features (e.g. a particular Shader), carefully
# consider, on a case-by-case basis, whether it is better to not export the
# containing object (i.e. treat the object as unsupported) or to just not
# export that single features.  For the latter case, it's good practice to
# write a warning to stdout.
#
# When getting the mesh to work with from Blender, make sure to use
# ...getMesh(False, True), or the equivalent ...getMesh(mesh=True).
# This will get a Blender "wrapped" Mesh instance instead of a non-wrapped
# NMesh instance (contrary to the wrapping we are doing here, Blender's
# "wrapping" actually puts you closer to the physical data).
# The parent/child relationships between these wrapper classes reflects
# scene node relationships, not Blender's explicit parenting relationships.
# For example, Blender Objects aggregate Meshes and Mesh references, but do
# not consider them children; but in JME, nodes can have nodes and Meshes
# (or any other Spatials) as children.
#
# Consider limiting vertex transformations (thereby losing useful node
# transformations by checking Object.upAxis (read-only attr.)


class UnsupportedException(Exception):
    def __init__(self, setting, val=None, note=None):
        Exception.__init__(self)
        if val == None:
            self.msg = ("Feature '" + setting + "' is unsupported.")
        else:
            self.msg = ("Value '" + str(val) + "' for setting '" + setting
                    + "' unsupported.")
        if note != None: self.msg += ("  " + note)

    def __str__(self):
        return self.msg


from Blender.Object import PITypes as _bPITypes
class JmeNode(object):
    __slots__ = ('wrappedObj', 'children', 'jmeMats', 'jmeTextureState',
            'name', 'autoRotate', 'backoutTransform')
    IDENTITY_4x4 = _bmath.Matrix().resize4x4()
    BLENDER_TO_JME_ROTATION = _bmath.RotationMatrix(-90, 4, 'x')

    def __init__(self, bObjOrName, nodeTree=None):
        """Assumes input Blender Object already validated, like by using the
        supported static method below.
        I.e., is of supported type, and facing method is supported.
        Materials from given bObj and direct data mesh (if any) will be added
        to one of the specified nodeTree's materials maps."""
        object.__init__(self)
        self.children = None
        self.wrappedObj = None
        self.autoRotate = False
        self.backoutTransform = None
        self.jmeMats = None
        self.jmeTextureState = None

        if isinstance(bObjOrName, basestring):
            self.name = bObjOrName
            return

        if nodeTree == None:
            raise Exception("If instantiating a Blender-Object-wrapping Node, "
                    + "param nodeTree must be set")
        self.wrappedObj = bObjOrName
        self.name = self.wrappedObj.name
        bMesh = self.wrappedObj.getData(False, True)
        twoSided = bMesh != None and (bMesh.mode & _meshModes['TWOSIDED'])
        if len(self.wrappedObj.getMaterials()) > 0:
            self.jmeMats = []
            jmeTexs = []
            for bMat in self.wrappedObj.getMaterials():
                self.jmeMats.append(nodeTree.includeMat(bMat, twoSided))
                for j in bMat.enabledTextures:
                    try:
                        JmeTexture.supported(bMat.textures[j])
                        jmeTexs.append(nodeTree.includeTex(bMat.textures[j]))
                    except UnsupportedException, ue:
                        print ("Skipping a texture of object " + self.name
                                + " due to: " + str(ue))
            if len(jmeTexs) > 0:
                self.jmeTextureState = nodeTree.includeJmeTextureList(jmeTexs)
        if bMesh == None: return

        # From here on, we know we have a Blender direct Mesh data member
        objColor = None
        try:
            objColor = self.wrappedObj.color
        except Exception, e:
            print str(e)  # For some reason, sometimes the .color attribute is
                          # available, and sometimes it is not.
        jmeMesh =  JmeMesh(bMesh, objColor)
        self.addChild(jmeMesh)
        #print "Instantiated JmeNode '" + self.getName() + "'"
        # Since Blender has mashed together the Object and Mesh by having
        # object.colbits specify how the Mesh's materials are to be
        # interpreted, we add the Mesh's materials and textures here.
        meshMats = []
        jmeTexs = []
        for i in range(len(bMesh.materials)):
            #print "Bit " + str(i) + " for " + self.getName() + " = " + str(self.wrappedObj.colbits & (1<<i))
            if 0 != (self.wrappedObj.colbits & (1<<i)): continue
            if bMesh.materials[i] == None: continue
              # This will happen if the mat has been removed
            meshMats.append(nodeTree.includeMat(bMesh.materials[i], twoSided))
            for j in bMesh.materials[i].enabledTextures:
                try:
                    JmeTexture.supported(bMesh.materials[i].textures[j])
                    jmeTexs.append(nodeTree.includeTex(
                            bMesh.materials[i].textures[j]))
                except UnsupportedException, ue:
                    print ("Skipping a texture of mesh " + jmeMesh.getName()
                            + " due to: " + str(ue))
        if len(meshMats) > 0: jmeMesh.jmeMats = meshMats
        if len(jmeTexs) > 0:
            jmeMesh.jmeTextureState = nodeTree.includeJmeTextureList(jmeTexs)

    def addChild(self, child):
        if self.children == None: self.children = []
        self.children.append(child)

    def getName(self): return self.name

    def getXmlEl(self):
        tag = _XmlTag('com.jme.scene.Node', {'name':self.getName()})

        if self.jmeMats != None:
            rsTag = _XmlTag('renderStateList')
            for mat in self.jmeMats: rsTag.addChild(mat.getXmlEl())
            if self.jmeTextureState != None:
                rsTag.addChild(self.jmeTextureState.getXmlEl())
            tag.addChild(rsTag)

        if self.children != None:
            childrenTag = _XmlTag('children', {'size':len(self.children)})
            tag.addChild(childrenTag)
            for child in self.children:
                if self.wrappedObj != None and not isinstance(child, JmeMesh):
                    child.backoutTransform = self.wrappedObj.mat
                    # N.b. DO NOT USE .matrixParentInverse.  That is a static
                    #  value for funky Blender behaior we don't want to retain.
                childrenTag.addChild(child.getXmlEl())

        if self.wrappedObj == None: return tag

        if self.backoutTransform == None:
            matrix = self.wrappedObj.mat
        else:
            matrix = self.wrappedObj.mat * self.backoutTransform.copy().invert()

        # Set local variables just to reduce typing in this block.
        loc = matrix.translationPart()
        if (round(loc[0], 6) == 0. and round(loc[1], 6) == 0.
                and round(loc[2], 6) == 0.): loc = None
        # N.b. Blender.Mathutils.Quaternines ARE NOT COMPATIBLE WITH jME!
        e = matrix.toEuler()
        if round(e.x, 6) == 0 and round(e.y, 6) == 0 and round(e.z, 6) == 0:
            rQuat = None
            scaleMat = matrix
        else:
            # Blender Quaternion functions give different results from the
            # algorithms at euclideanspace.com, especially for the X rot
            # element.  However, until I don't want to introduce the risk of
            # several new ESQuaternion methods until I am certain that we can
            # successfully match Ogre exporte behavior with Blender's quats.
            #rQuat = _esmath.ESQuaternion(e, True)
            rQuat = matrix.toQuat()
            scaleMat = matrix * rQuat.copy().inverse().toMatrix().resize4x4()
        scale = (scaleMat[0][0], scaleMat[1][1], scaleMat[2][2])
        if (round(scale[0], 6) == 1.
                and round(scale[1], 6) == 1. and round(scale[2], 6) == 1.):
            scale = None
        if self.autoRotate:
            raise Exception("Have not refactored AUTOROTATE mode yet")
        # Need to add the attrs sequentially in order to preserve sequence
        # of the attrs in the output.
        if loc != None:
            locTag = _XmlTag("localTranslation")
            locTag.addAttr("x", loc[0], 6)
            locTag.addAttr("y", loc[1], 6)
            locTag.addAttr("z", loc[2], 6)
            tag.addChild(locTag)
        if rQuat != None:
            locTag = _XmlTag("localRotation")
            locTag.addAttr("x", rQuat.x, 6)
            locTag.addAttr("y", rQuat.y, 6)
            locTag.addAttr("z", rQuat.z, 6)
            locTag.addAttr("w", rQuat.w, 6)
            tag.addChild(locTag)
        if scale != None:
            locTag = _XmlTag("localScale")
            locTag.addAttr("x", scale[0], 6)
            locTag.addAttr("y", scale[1], 6)
            locTag.addAttr("z", scale[2], 6)
            tag.addChild(locTag)
        return tag

    def getType(self):
        return self.wrappedObj.type

    def supported(bObj, skipObjs):
        """Static method returns 0 if type not supported; non-0 if supported.
           2 if will require face niggling; 3 if faceless"""
        # Silently ignore keyframes bMes.key for now.
        # Is face transp mode bMesh.mode for design-time usage?
        # Ignore animation, action, constraints, ip, and keyframing settings.
        # Users should know that we don't support them.

        if bObj.type not in ['Mesh', 'Armature']: return 0
        if bObj.type == 'Armature':
            arma = bObj.getData(False, True)
            if arma.vertexGroups:
                print "Vertex Group weighting not supported yet"
                return 0
            if arma.envelopes:
                print "Envelope weighting not supported yet"
                return 0
            for bone in arma.bones.values():
                if _Armature.HINGE in bone.options:
                    print "HINGE bone option not supported"
                    return 0
            return True
        bMesh = bObj.getData(False, True)
        if not bMesh: raise Exception("Mesh Object has no data member?")
        if bMesh.multires:
            print "multires data"
            return 0
        if skipObjs:
            try:
                if len(bObj.getMaterials()) > 0:
                    for bMat in bObj.getMaterials():
                        JmeMaterial(bMat, False) # twoSided param doesn't matter
                        for j in bMat.enabledTextures:
                            JmeTexture.supported(bMat.textures[j])
                for i in range(len(bMesh.materials)):
                    if 0 != (bObj.colbits & (1<<i)): continue
                    if bMesh.materials[i] == None: continue
                      # This will happen if the mat has been removed
                    JmeMaterial(bMesh.materials[i], False) # ditto
                    for j in bMesh.materials[i].enabledTextures:
                        JmeTexture.supported(bMesh.materials[i].textures[j])
                # Following test was misplaced, because the nodes with the
                # texcoords may be descendants, not necessarily "this" node.
                #if anyTextures and (not bMesh.vertexUV) and not bMesh.faceUV:
                    #raise UnsupportedException(
                            #"We only support UV for texture mapping, and "
                            #+ "neither sticky nor face texcoords are set")
            except UnsupportedException, ue:
                print ue
                return 0
        if bMesh.texMesh != None:
            print "Texture coords by Mesh-ref"
            return 0
        if bMesh.faceUV and bMesh.vertexUV:
            print "Mesh contains both sticky and per-face texture coords"
            return 0
        if bObj.isSoftBody:
            print "WARNING:  Soft Body settings not supported yet.  Ignoring."
        if bObj.piType != _bPITypes['NONE']:
            print "WARNING:  Particle Interation not supported yet.  Ignoring."
        if bObj.rbMass != 1.0 or bObj.rbRadius != 1.0:
            print "WARNING:  Rigid Body settings not supported yet.  Ignoring."
            # Can't test .rbFlags, since they are on and significant by dflt.
            # Can't test .rbShapeBoundType, since there is a constant with
            # value 0.  Poorly designed constants.
        if bObj.track != None:
            print "WARNING: Object tracking not supported yet.  Ignoring."
        vpf = JmeMesh.vertsPerFace(bObj.getData(False, True).faces)
        if vpf == None:
            print "FYI:  Accepting object '" + bObj.name + "' with no faces"
            return 3
        if vpf == set([0]):
            print "FYI:  Accepting object '" + bObj.name + "' with 0 vert faces"
            return 3
        if vpf == set([3,4]) or vpf == set([0,3,4]):
            print ("FYI:  Object '" + bObj.name
                    + "' accepted but will require unification to Trimeshes")
            return 2
        if (vpf == set([3,0]) or vpf == set([0,4])
                or vpf == set([3]) or vpf == set([4])): return 1
        print ("FYI:  Refusing object '" + bObj.name
                + "' because unsupported vertexes-per-face: " + str(vpf))
        return 0

    def __str__(self):
        return '[' + self.getName() + ']'

    def __repr__(self):
        return "<JmeNode> " + self.__str__()

    supported = staticmethod(supported)


class JmeMesh(object):
    __slots__ = ('wrappedMesh', 'jmeMats', 'jmeTextureState',
            '__vpf', 'defaultColor', 'name', 'autoRotate')
    # defaultColor corresponds to jME's Meshs' defaultColor.
    # In Blender this is a per-Object, not per-Mesh setting.
    # This is why it is a parameter of the constructor below.

    def __init__(self, bMesh, color=None):
        """Assumes input Blender Mesh already validated, like by using the
        vertsPerFace static method below.
        I.e., is of supported type, and facing method is supported.
        The color setting should come from the parent Blender Object's
        .color setting."""
        object.__init__(self)
        self.wrappedMesh = bMesh
        self.name = bMesh.name
        self.defaultColor = color
        self.autoRotate = False
        self.jmeMats = None
        self.jmeTextureState = None
        #print "Instantiated JmeMesh '" + self.getName() + "'"
        self.__vpf = JmeMesh.vertsPerFace(self.wrappedMesh.faces)

    def getName(self): return self.name

    def getXmlEl(self):
        if self.wrappedMesh.verts == None:
            raise Exception("Mesh '" + self.getName() + "' has no vertexes")
        mesh = self.wrappedMesh.copy()
        # This does do a deep copy! (like we need)
        if self.autoRotate: raise Exception("AUTOROTATE not impd yet")
        # Note that the last param here doesn't calculate norms anew, it just
        # transforms them along with vertexes, which is just what we want.
        unify = 3 in self.__vpf and 4 in self.__vpf
        if 4 in self.__vpf and not unify:
            meshType = 'Quad'
        else:
            meshType = 'Tri'
        # TODO:  When iterate through verts to get vert vectors + normals,
        #        do check for None normal and throw if so:
        #   raise Exception("Mesh '"
        #       + self.wrappedMesh.name + "' has a vector with no normal")
        #   This is a Blender convention, not a 3D or JME convention
        #   (requirement for normals).
        tag = _XmlTag('com.jme.scene.' + meshType + 'Mesh',
                {'name':self.getName()})
        if (self.defaultColor != None and
            (self.defaultColor[0] != 1 or self.defaultColor[1] != 1
                or self.defaultColor[2] != 1 or self.defaultColor[3] != 1)):
            colorTag = _XmlTag("defaultColor")
            tag.addChild(colorTag)
            colorTag.addAttr("r", self.defaultColor[0])
            colorTag.addAttr("g", self.defaultColor[1])
            colorTag.addAttr("b", self.defaultColor[2])
            colorTag.addAttr("a", self.defaultColor[3])

        if self.jmeMats != None:
            rsTag = _XmlTag('renderStateList')
            for mat in self.jmeMats: rsTag.addChild(mat.getXmlEl())
            tag.addChild(rsTag)
            if self.jmeTextureState != None:
                rsTag.addChild(self.jmeTextureState.getXmlEl())

        # Make a copy so we can easily add verts like a normal Python list
        vertList = []
        for v in mesh.verts: vertList.append(v)
        vertToColor = None
        vertToUv = None
        faceVertToNewVert = [] # Direct replacement for face[].verts[].index
         # 2-dim array. Only necessary (and only changed) if using vertexColors.
         # Note that though faceVertToNewVert face count and vert count always
         # exactly matches the source mesh.faces.  We just change the
         # destination indexes.
        if mesh.vertexColors:
            vertToColor = {} # Simple modifiedVertIndex -> Color Hash
            #  Temp vars only used in this block:
            origIndColors = {}
            # Nested dict. from OrigIndex -> Color -> NewIndex

            # TODO:  Test for objects with no faces, like curves, points.
            for face in mesh.faces:
                if face.verts == None: continue
                # The face.col reference in the next line WILL THROW
                # if the mesh does not support vert colors
                # (i.e. mesh.vertexColors).
                if len(face.verts) != len(face.col):
                    raise Exception(
                    "Counts of Face vertexes and vertex-colors do not match: "
                        + str(len(face.verts)) + " vs. " + str(len(face.col)))
                if len(face.verts) < 1: continue
                faceVertToNewVert.append([])
                for i in range(len(face.verts)):
                    colKey = (str(face.col[i].r)
                            + "|" + str(face.col[i].g)
                            + "|" + str(face.col[i].b)
                            + "|" + str(face.col[i].a))
                    # Generate key from Color since equality is not implemented
                    # properly for MCols.  I.e. "in" tests fail, etc.
                    if face.verts[i].index in origIndColors:
                        #print ("Checking for " + colKey + " in "
                                #+ str(origIndColors[face.verts[i].index]))
                        if colKey in origIndColors[face.verts[i].index]:
                            #print ("Agreement upon color " + colKey
                                    #+ " for 2 face verts")
                            finalFaceVIndex = \
                              origIndColors[face.verts[i].index][colKey]
                        else:
                            # CREATE NEW VERT COPY!!
                            finalFaceVIndex = len(vertList)
                            vertList.append(UpdatableMVert(face.verts[i],
                                    finalFaceVIndex, mesh))
                            origIndColors[face.verts[i].index][colKey] =\
                                    finalFaceVIndex
                            # Writing the new vert index to the map-map so that
                            # other faces using the same color of the same
                            # original index may re-use it (preceding if block)
                    else:
                        # Only use of vertex (so far), so just save orig index
                        finalFaceVIndex = face.verts[i].index
                        origIndColors[face.verts[i].index] = \
                                { colKey:finalFaceVIndex }
                        # Writing the existing vert index to the map-map so
                        # that other faces using the same color of the same
                        # original index may re-use it.
                    vertToColor[finalFaceVIndex] = face.col[i]
                    faceVertToNewVert[-1].append(finalFaceVIndex)
        else:
            for face in mesh.faces:
                if face.verts == None or len(face.verts) < 1: continue
                faceVertToNewVert.append([])
                for i in range(len(face.verts)):
                    faceVertToNewVert[-1].append(face.verts[i].index)
        # At this point, faceVertToNewVert[][]  contains references to every
        # vertex, both original and new copies.  For shared vertexes, there
        # will be multiple faceVertToNewVert[][] elements pointing to the
        # same vertex, but there will be no vertexes orphaned by faceVert...
        if mesh.faceUV:
            vertToUv = {} # Simple modifiedVertIndex -> [u,v] Vector
            #  Temp vars only used in this block:
            origIndUvs = {}
            # Nested dict. from OrigIndex -> "u|v" -> NewIndex

            # TODO:  Test for objects with no faces, like curves, points.
            firstUvVertexCopy = len(vertList)
            for face in mesh.faces:
                if face.verts == None: continue
                # The face.uv reference in the next line WILL THROW
                # if the mesh does not support uv values
                # (i.e. mesh.faceUV).
                if (len(face.verts) != len(face.uv)):
                    raise Exception(
                    "Counts of Face vertexes and uv-values do not match: "
                        + str(len(face.verts)) + " vs. " + str(len(face.uv)))
                for i in range(len(face.verts)):
                    uvKey = str(face.uv[i].x) + "|" + str(face.uv[i].y)
                    # Compound key to prevent need for nested or 2-dim hash
                    # N.b. we generate the uvKey from the original face data,
                    # since nothing above this level gets changed.
                    vertIndex = faceVertToNewVert[face.index][i]
                    if vertIndex in origIndUvs:
                        if uvKey in origIndUvs[vertIndex]:
                            #print ("Agreement upon uv " + uvKey
                                    #+ " for 2 face verts")
                            finalFaceVIndex = origIndUvs[vertIndex][uvKey]
                        else:
                            # CREATE NEW VERT COPY!!
                            finalFaceVIndex = len(vertList)
                            vertList.append(UpdatableMVert(
                                vertList[vertIndex], finalFaceVIndex, mesh))
                            origIndUvs[vertIndex][uvKey] = finalFaceVIndex
                            # Writing the new vert index to the map-map so that
                            # other faces using the same uv val of the same
                            # original index may re-use it (preceding if block)
                            if vertToColor != None:
                                # Must make a vertToColor mapping for any
                                # new vert.
                                if vertList[-1].origIndex in vertToColor:
                                    vertToColor[finalFaceVIndex] =  \
                                            vertToColor[vertList[-1].origIndex]
                                else:
                                    print ("WARNING:  Original vert "
                                        + str(vertList[-1].origIndex)
                                        + " which was dupped for faceUV, was "
                                        + "assigned no vertex color")
                        faceVertToNewVert[face.index][i] = finalFaceVIndex
                        # Overwriting faceVertToNewVert from vertIndex
                    else:
                        # Only use of vertex (so far), so just save orig index
                        finalFaceVIndex = vertIndex
                        origIndUvs[vertIndex]= { uvKey:finalFaceVIndex }
                        # Writing the existing vert index to the map-map so
                        # that other faces using the same uv val of the same
                        # original index may re-use it.
                    vertToUv[finalFaceVIndex] = face.uv[i]

        if len(mesh.verts) != len(vertList):
            print (str(len(vertList) - len(mesh.verts)) + " verts added:  "
                    + str(len(mesh.verts)) + " -> " + str(len(vertList)))
        coArray = []
        noArray = []
        if vertToColor == None:
            colArray = None
        else:
            colArray = []
        if mesh.faceUV or mesh.vertexUV:
            texArray=[]
        else:
            texArray = None
        nonFacedVertexes = 0
        nonUvVertexes = 0
        for v in vertList:
            coArray.append(v.co.x)
            coArray.append(v.co.y)
            coArray.append(v.co.z)
            noArray.append(v.no.x)
            noArray.append(v.no.y)
            noArray.append(v.no.z)
            # Blender treats +v as up.  That makes sense with gui programming,
            # but the "v" of "uv" goes + down, so we have to correct this.
            # (u,v) = (0,0) = TOP LEFT.
            # This is why both v values are saved as 1 - y.
            if colArray != None:
                if v.index in vertToColor:
                    colArray.append(vertToColor[v.index])
                else:
                    nonFacedVertexes += 1
                    colArray.append(None)  # We signify WHITE by None
            if mesh.vertexUV: 
                # For unknown reason, Blender's Sticky uv vert creation sets
                # values to (-1 to 1) range instead of proper (0 to 1) range.
                texArray.append(v.uvco.x * .5 + .5)
                texArray.append(1. - (v.uvco.y * .5 + .5))
            elif mesh.faceUV: 
                if v.index in vertToUv:
                    uvVert = vertToUv[v.index]
                    texArray.append(uvVert.x)
                    texArray.append(1 - uvVert.y)
                else:
                    nonUvVertexes += 1
                    texArray.append(-1)
                    texArray.append(-1)
        if nonFacedVertexes > 0:
            print ("WARNING: " + str(nonFacedVertexes)
                + " vertexes set to WHITE because no face to derive color from")
        if nonUvVertexes > 0:
            print ("WARNING: " + str(nonUvVertexes)
                + " uv vals set to (-1,-1) because no face to derive uv from")

        vertTag = _XmlTag("vertBuf", {"size":len(coArray)})
        vertTag.addAttr("data", coArray, 6, 3)
        tag.addChild(vertTag)
        normTag = _XmlTag("normBuf", {"size":len(noArray)})
        normTag.addAttr("data", noArray, 6, 3)
        tag.addChild(normTag)
        if texArray != None:
            coordsTag = _XmlTag("coords", {"size":len(texArray)})
            coordsTag.addAttr("data", texArray, 6, 3)
            texCoordsTag = _XmlTag("com.jme.scene.TexCoords", {"perVert":2})
            texCoordsTag.addChild(coordsTag)
            texTag = _XmlTag("texBuf", {"size":1})
            texTag.addChild(texCoordsTag)
            tag.addChild(texTag)
        if colArray != None:
            rgbaArray = []
            for c in colArray:
                if c == None:
                    rgbaArray.append(1)
                    rgbaArray.append(1)
                    rgbaArray.append(1)
                    rgbaArray.append(1)
                else:
                    rgbaArray.append(c.r/255.)
                    rgbaArray.append(c.g/255.)
                    rgbaArray.append(c.b/255.)
                    rgbaArray.append(c.a/255.)
            vertColTag = _XmlTag("colorBuf", {"size":len(rgbaArray)})
            vertColTag.addAttr("data", rgbaArray, 3, 4)
            tag.addChild(vertColTag)
        if 3 not in self.__vpf and 4 not in self.__vpf: return tag
        faceVertIndexes = []
        for i in range(len(faceVertToNewVert)):
            if unify and len(faceVertToNewVert[i]) == 4:
                faceVertIndexes.append(faceVertToNewVert[i][0])
                faceVertIndexes.append(faceVertToNewVert[i][1])
                faceVertIndexes.append(faceVertToNewVert[i][2])
                faceVertIndexes.append(faceVertToNewVert[i][0])
                faceVertIndexes.append(faceVertToNewVert[i][2])
                faceVertIndexes.append(faceVertToNewVert[i][3])
            else:
                for j in range(len(faceVertToNewVert[i])):
                    faceVertIndexes.append(faceVertToNewVert[i][j])
        indTag = _XmlTag("indexBuffer", {"size":len(faceVertIndexes)})
        if len(face.verts) == 4 and not unify: outputVpf = 4
        else: outputVpf = 3
        indTag.addAttr("data", faceVertIndexes, None, outputVpf)
        tag.addChild(indTag)
        return tag

    def vertsPerFace(faces):
        """Static method returns 0 if type not supported; non-0 if supported.
           2 if will require face niggling; 3 if faceless"""
        if faces == None: return None
        facings = set()
        for f in faces:
            if f.verts == None: raise Exception("Face with no vertexes?")
            facings.add(len(f.verts))
        return facings

    vertsPerFace = staticmethod(vertsPerFace)


class JmeBone(object):
    # TODO:  As each bone consists of a single vertex, I am hoping that we
    # don't need to do any baking.
    # Could be that the weigthing vector will need to be transformed similarly
    # though.
    """We make a top level Bone for the entire Armature, for which Blender has
    no corresponding bone.  This is necessary since Blender can have
    "unparented" bones, but JME requires all but the root bone to be
    parented."""
    __slots__ = ('matrix', 'children', 'name', 'autoRotate',
            'childTransOffset', 'parent', 'headLoc', 'retainTransform')
    # The childTranOffset is a translation added to the translation of all
    # direct child bones.  Since Blender is calculating the vertex weights
    # of the skins, this is the only remaining significance of a bone's
    # length.

    def __init__(self, objOrBone, parent=None):
        object.__init__(self)
        self.autoRotate = False
        blenderChildren = []
        self.children = None
        self.retainTransform = None
        if parent == None:
            if isinstance(objOrBone, _Armature.Bone):
                raise Exception("Parent not specified for internal Bone")
            self.parent = None
            self.headLoc = None
            self.matrix = _bmath.Matrix(objOrBone.matrixLocal)
            if self.matrix != JmeNode.IDENTITY_4x4:
                # BAKE IN ANY NODE ROTATION TRANSFORMATION
                # Make 4x4 matrix out of JUST rotation portion of matrixLocal
                meshBakeTransform = self.matrix.rotationPart().resize4x4()
                # Wipe the rotation portion of matrixLocal.
                # Unfortunately, this competely hoses the translation row,
                # so save off the properly rotated translation vector:
                translationRow = self.matrix[3]
                # This is because the inversion hoses the translation part
                derot = self.matrix * _bmath.Matrix(meshBakeTransform).invert()
                self.matrix = _bmath.Matrix(
                        derot[0], derot[1], derot[2], translationRow)
            arma = objOrBone.getData(False, True)
            self.name = arma.name
            self.childTransOffset = 0
            for childBlenderBone in arma.bones.values():
                if childBlenderBone.parent == None:
                    blenderChildren.append(childBlenderBone)
        else:
            if not isinstance(objOrBone, _Armature.Bone):
                raise Exception("Internal bone object is not a Blender Bone: "
                        + str(type(objOrBone)))
            self.parent = parent
            self.headLoc = _bmath.Vector(objOrBone.head['BONESPACE'])
            self.matrix = _bmath.Matrix(objOrBone.matrix['BONESPACE'])
            blenderChildren = objOrBone.children
            self.childTransOffset = objOrBone.length
            self.name = objOrBone.name
        if len(blenderChildren) < 1: return
        # Recursive instantiation:
        self.children = []
        for blenderBone in blenderChildren:
            self.children.append(JmeBone(blenderBone, self))

    def getName(self):
        return self.name

    def getXmlEl(self):
        tag = _XmlTag('com.jme.animation.Bone', {'name':self.getName()})
        # Do all work with a copy.  We don't modify user data.
        if self.autoRotate:
            # Need to transform the entire matrixLocal.
            self.matrix = self.matrix * JmeNode.BLENDER_TO_JME_ROTATION

        if self.children != None:
            childrenTag = _XmlTag('children', {'size':len(self.children)})
            tag.addChild(childrenTag)
            for child in self.children:
                childrenTag.addChild(child.getXmlEl())

        matrix = self.matrix
        if self.retainTransform != None: matrix = matrix * self.retainTransform
        # Set local variables just to reduce typing in this block.
        if self.headLoc == None:
            loc = matrix.translationPart()
        else:
            loc = self.headLoc
            loc.z += self.parent.childTransOffset
        # N.b. Blender.Mathutils.Quaternines ARE NOT COMPATIBLE WITH jME!
        e = matrix.toEuler()
        if round(e.x, 6) == 0 and round(e.y, 6) == 0 and round(e.z, 6) == 0:
            rQuat = None
        else:
            rQuat = _esmath.ESQuaternion(e, True)
        #else: rQuat = self.wrappedObj.rot.toQuat()
        scale = matrix.scalePart()
        # Need to add the attrs sequentially in order to preserve sequence
        # of the attrs in the output.
        if loc != None and (round(loc[0], 6) != 0. or round(loc[1], 6) != 0.
                or round(loc[2], 6) != 0.):
            locTag = _XmlTag("localTranslation")
            locTag.addAttr("x", loc[0], 6)
            locTag.addAttr("y", loc[1], 6)
            locTag.addAttr("z", loc[2], 6)
            tag.addChild(locTag)
        if rQuat != None:
            locTag = _XmlTag("localRotation")
            locTag.addAttr("x", rQuat.x, 6)
            locTag.addAttr("y", rQuat.y, 6)
            locTag.addAttr("z", rQuat.z, 6)
            locTag.addAttr("w", rQuat.w, 6)
            tag.addChild(locTag)
        if scale != None and (round(scale[0], 6) != 1.
                or round(scale[1], 6) != 1. or round(scale[2], 6) != 1.):
            locTag = _XmlTag("localScale")
            locTag.addAttr("x", scale[0], 6)
            locTag.addAttr("y", scale[1], 6)
            locTag.addAttr("z", scale[2], 6)
            tag.addChild(locTag)
        return tag


class JmeBoneContainer(object):
    """We make a top level Bone for the entire Armature, for which Blender has
    no corresponding bone.  This is necessary since Blender can have
    "unparented" bones, but JME requires all but the root bone to be
    parented."""
    __slots__ = ('wrappedObj', 'wrappedArma', 'retainTransform',
            'boneTree', 'autoRotate', 'name', 'children')
    # Children is only used to tree recursion can descend into the bones
    # autoRotate and retainTransform attrs are hacks just to pass directly to
    # the root boneTree instance.

    def __init__(self, bObj):
        """N.b. the bObj param is not the data object (like we take for Mesh
        Objects), but a Blender Object."""
        object.__init__(self)
        self.autoRotate = False
        self.wrappedObj = bObj
        self.wrappedArma = bObj.getData(False, True)
        self.boneTree = JmeBone(bObj)
        self.children = [self.boneTree]
        self.retainTransform = None

    def getXmlEl(self):
        self.boneTree.autoRotate = self.autoRotate
        self.boneTree.retainTransform = self.retainTransform
        return self.boneTree.getXmlEl()


class NodeTree(object):
    """Trivial tree dedicated for JmeNode and JmeBoneContainer members.
    Add all members to the tree, then call nest().
    See method descriptions for details."""

    __slots__ = ('__memberMap', '__memberKeys',
            '__matMap1side', '__matMap2side', 'root',
            '__textureHash', '__textureStates')
    # N.b. __memberMap does not have a member for each node, but a member
    #      for each saved Blender object.
    # __memberKey is just because Python has no ordered maps/dictionaries
    # We want nodes persisted in a well-defined sequence.
    # __textureHash is named *Hash instead of *Map only to avoid confusion
    # with "texture maps", which these are not.

    def __init__(self):
        object.__init__(self)
        self.__memberMap = {}
        self.__memberKeys = []
        self.__matMap1side = {}
        self.__matMap2side = {}
        self.__textureHash = {}
        self.__textureStates = set()
        self.root = None

    def includeTex(self, mtex):
        """include* instead of add*, because we don't necessarily 'add'.  We
        will just increment the refCount if it's already in our list.
        Returns new or used JmeTexture."""
        newJmeTexId = JmeTexture.idFor(mtex)
        if newJmeTexId in self.__textureHash:
            jmeTex = self.__textureHash[newJmeTexId]
            jmeTex.refCount += 1
            return jmeTex
        jmeTex = JmeTexture(mtex, newJmeTexId)
        self.__textureHash[newJmeTexId] = jmeTex
        return jmeTex

    def includeJmeTextureList(self, textureList):
        """include* instead of add*, because we don't necessarily 'add'.  We
        will just increment the refCount if it's already in our list.
        Returns new or used JmeTextureState."""
        for texState in self.__textureStates:
            if texState.cf(textureList):
                texState.refCount += 1
                return texState
        texState = JmeTextureState(textureList)
        self.__textureStates.add(texState)
        return texState

    def includeMat(self, bMat, twoSided):
        """include* instead of add*, because we don't necessarily 'add'.  We
        will just increment the refCount if it's already in our list.
        Returns new or used JmeMaterial."""
        if twoSided:
            matMap = self.__matMap2side
        else:
            matMap = self.__matMap1side
        if bMat in matMap:
            jmeMat = matMap[bMat]
            jmeMat.refCount += 1
            return jmeMat
        jmeMat = JmeMaterial(bMat, twoSided)
        matMap[bMat] = jmeMat
        return jmeMat

    def addIfSupported(self, blenderObj, skipObjs):
        """Creates a JmeNode or JmeBoneContainer for the given Blender Object,
        if the Object is supported."""
        if not JmeNode.supported(blenderObj, skipObjs): return
        if blenderObj.type == "Armature":
            self.__memberMap[blenderObj] = JmeBoneContainer(blenderObj)
        else:
            self.__memberMap[blenderObj] = JmeNode(blenderObj, self)
        self.__memberKeys.append(blenderObj)

    def __uniquifyNames(node, parentName, nameSet):
        """Static private method"""
        # Would like to rename nodes ealier, to that messages (error and
        # otherwise) could reflect the new names, but we can't nest properly
        # until all nodes are added to the tree, and we want tree organization
        # to determine naming precedence.
        if not isinstance(node, JmeBoneContainer):
            if node.name == None:
                raiseException("Node in tree without name!")
            #print "Checking name " + node.name + "..."
            if node.name in nameSet:
                #print "Renaming 2nd node with name " + node.name + "..."
                # TODO:  Make the checks for existing substrings case-insens.
                if (isinstance(node, JmeMesh) and parentName != None
                        and (parentName + "Mesh") not in nameSet):
                    node.name = (parentName + "Mesh")
                elif (isinstance(node, JmeMesh) and node.name.count("Mesh") < 1
                        and (node.name + "Mesh") not in nameSet):
                    node.name += "Mesh"
                elif (isinstance(node, JmeNode) and node.name.count("Node") < 1
                        and (node.name + "Node") not in nameSet):
                    node.name += "Node"
                else:
                    node.name += ".uniqd"
                    while node.name in nameSet: node.name += ".uniqd"
            nameSet.add(node.name)
        if (isinstance(node, JmeMesh)) or node.children == None: return
        if isinstance(node, JmeBoneContainer):
            nameToPass = None
        else:
            nameToPass = node.name
        for child in node.children:
            NodeTree.__uniquifyNames(child, nameToPass, nameSet)

    def nest(self):
        """addChild()s wherever the wrappedObj's parent is present; adds all
        remaining nodes to the top level; and enforces the tree has a single
        root by adding a top grouping node if necessary.
        Returns the root node."""

        if len(self.__memberKeys) < 1:
            self.root = None
            return self.root
        for bo in self.__memberKeys:
            if bo.parent != None and bo.parent in self.__memberMap:
                print bo.getName() + " hasa parent"
                self.__memberMap[bo.parent].addChild(self.__memberMap[bo])
                del self.__memberMap[bo]
            else:
                print bo.getName() + " has NO parent"
        for key in self.__memberKeys[:]:
            if key not in self.__memberMap: self.__memberKeys.remove(key)
        if len(self.__memberKeys) < 1:
            raise Exception("Internal problem.  Tree ate itself.")
        if len(self.__memberKeys) < 2:
            self.root = self.__memberMap.popitem()[1]
            del self.__memberKeys[0]
        else:
            self.root = JmeNode("BlenderObjects")
            for key in self.__memberKeys:
                self.root.addChild(self.__memberMap[key])
        NodeTree.__uniquifyNames(self.root, None, set())
        return self.root

    def getXml(self):
        if self.root == None and self.nest() == None: return None
        for m in self.__matMap1side.itervalues(): m.written = False
        for m in self.__matMap2side.itervalues(): m.written = False
        for t in self.__textureHash.itervalues(): m.written = False
        for ts in self.__textureStates: ts.written = False
        return self.root.getXmlEl()

    __uniquifyNames = staticmethod(__uniquifyNames)


from Blender.Material import Shaders as _bShaders
from bpy.data import scenes as _bScenes
class JmeMaterial(object):
    # May or may not need to redesign with subclasses to handle textures and
    # other material states that are not simply the 4 colors + 2 states + shini.
    "A material definition corresponding to a jME MaterialState."

    __slots__ = ('colorMaterial', 'ambient', 'emissive', 'diffuse', 'written',
            'specular', 'shininess', 'materialFace', 'refCount', 'blenderName')
    AMBIENT_OBJDIF_WEIGHTING = .7
    # This has no effect if Blender World ambient lighting is active.
    # If inactive, this specifies the portion of the generated material ambient
    # color from the material's diffuse color.  The remainder
    # (1.0 - ...WEIGHTING) is white.  This is before the total effect is
    # diminished according to the Blender Material's .amb value.

    def __init__(self, bMat, twoSided):
        "Throws a descriptive UnsupportedException for the obvious reason"

        object.__init__(self)
        self.written = False   # May write refs after written is True
        self.refCount = 0
        self.blenderName = bMat.name

        # Supportability validation
        #if len(bMat.colorband) > 0:  Attribute missing.
        # Would like to check validate the ObColor setting, but can't find it
        # in the API.
        if len(bMat.colorbandDiffuse) > 0:
            raise UnsupportedException("colorbandDiffuse", "any",
                    "colorbandDiffuse length: " + str(len(colorbandDiffuse)))
        if bMat.diffuseShader != _bShaders['DIFFUSE_LAMBERT']:
            raise UnsupportedException("diffuse shader", diffuseShader)
        if bMat.specShader != _bShaders['DIFFUSE_LAMBERT']:
            raise UnsupportedException("specular shader", specShader)
        if bMat.enableSSS:
            raise UnsupportedException("Subsurface Scattering (sss)")
        # Users should know that we don't support Mirroring, Halo, IPO,
        # lightGropus, etc., so we ignore all of these
        # Mirroring settings include Raytrace, Fresnel, Transp.
        # bMat.glossTra?
        if bMat.rbFriction != 0.5 or bMat.rbRestitution != 0:
            print "WARNING:  Rigid Body settings not supported yet.  Ignoring."
        if bMat.shadAlpha != 1.0:
            raise UnsupportedException("shadow alpha", bMat.shadAlpha)
        if bMat.specTransp != 1.0:
            raise UnsupportedException("specular transp.", bMat.specTransp)

        if bMat.mode & _matModes['VCOL_PAINT']:
            # TODO:  API says replaces "basic colors".  Need to verify that
            # that means diffuse, a.o.t. diffuse + specular + mirror.
            self.colorMaterial = "Diffuse"
        elif bMat.mode & _matModes['VCOL_LIGHT']:
            # TODO:  API says "add... as extra light".  ?  Test.
            # If by this they mean light-source-independent-light, then we
            # want to set this to "Ambient".
            self.colorMaterial = "AmbientAndDiffuse"
        else:
            self.colorMaterial = None
        self.diffuse = bMat.rgbCol
        self.diffuse.append(bMat.alpha)
        self.specular = bMat.specCol
        self.specular.append(bMat.alpha)
        #softnessPercentage = 1. - (bMat.hard - 1.) / 510.
        # Softness increases specular spread.
        # Unfortunately, it's far from linear, and the Python math functions
        # available are inadequate to normalize this to a ratio we can use.
        # Therefore, for now we are ignoring the harness setting.
        if (abs(bMat.hard - 50)) > 1:
            print ("WARNING: Hardness setting ignored.  " +
                    "Adjust spec setting to compensate")
        self.shininess = bMat.spec * .5 * 128
        if bMat.emit == 0.:
            self.emissive = None
        else:
            self.emissive = [bMat.rgbCol[0] * bMat.emit,
                    bMat.rgbCol[1] * bMat.emit,
                    bMat.rgbCol[2] * bMat.emit, bMat.alpha]
        if twoSided: self.materialFace = "FrontAndBack"
        else: self.materialFace = None

        # Ambient setting needs special attention.
        # Blender's ambient value applies the "World Ambient Light" color",
        # not any material color.  So, with a typical R=G=B color in Blender or
        # jME, this will "wash out" the material's explicitly set colors.
        # If the user has set the World ambient light color, this is probably
        # exactly what they want.  If the World ambient light is "off" (by
        # leaving the ambient light color at its default value of 0/0/0), then
        # the user probably has no idea that their explicit mat colors will
        # be weakened according to the mat's amb setting-- to the point
        # that if there is no light falling on the object, it will retain no
        # mat coloring.
        # Therefore, if World ambient light is off, we will make this washing
        # out effect more subtle, by combining diffuse + world lighting.
        world = _bScenes.active.world
        if world == None  or (
                world.amb[0] == 0 and world.amb[1] == 0 and world.amb[2] == 0):
            # Add some material coloring into ambient coloring.  Details above.
            # Weighted average of mat diffuse coloring + white (the white
            # portion will take the color of ambient-generating lights).
            # local vars just for conciseness.
            diffuseFactor = JmeMaterial.AMBIENT_OBJDIF_WEIGHTING
            whiteFactor = 1.0 - diffuseFactor
            self.ambient = [
                (diffuseFactor * self.diffuse[0] + whiteFactor) * bMat.amb,
                (diffuseFactor * self.diffuse[1] + whiteFactor) * bMat.amb,
                (diffuseFactor * self.diffuse[2] + whiteFactor) * bMat.amb,
                bMat.alpha]
        else:
            self.ambient = [bMat.amb, bMat.amb, bMat.amb, 1]

    def getXmlEl(self):
        tag = _XmlTag('com.jme.scene.state.MaterialState',
                {'class':"com.jme.scene.state.lwjgl.LWJGLMaterialState"})
        if self.written:
            tag.addAttr('ref', self.blenderName)
            return tag
        self.written = True
        #if self.refCount > 0: tag.addAttr("reference_ID", self.blenderName)
        tag.addAttr("reference_ID", self.blenderName)
        # Blender users have the ability to use these names, and to pull them
        # in from shared libraries, so it can be useful to propagate the names
        # even if not needed for our own refs.

        tag.addAttr("shininess", self.shininess, 2)
        if self.materialFace != None:
            tag.addAttr("materialFace", self.materialFace)
        if self.colorMaterial != None:
            tag.addAttr("colorMaterial", self.colorMaterial)
        diffuseTag = _XmlTag("diffuse")
        diffuseTag.addAttr("r", self.diffuse[0], 3)
        diffuseTag.addAttr("g", self.diffuse[1], 3)
        diffuseTag.addAttr("b", self.diffuse[2], 3)
        diffuseTag.addAttr("a", self.diffuse[3], 3)
        tag.addChild(diffuseTag)
        ambientTag = _XmlTag("ambient")
        ambientTag.addAttr("r", self.ambient[0], 3)
        ambientTag.addAttr("g", self.ambient[1], 3)
        ambientTag.addAttr("b", self.ambient[2], 3)
        ambientTag.addAttr("a", self.ambient[3], 3)
        tag.addChild(ambientTag)
        if self.emissive != None:
            emissiveTag = _XmlTag("emissive")
            emissiveTag.addAttr("r", self.emissive[0], 3)
            emissiveTag.addAttr("g", self.emissive[1], 3)
            emissiveTag.addAttr("b", self.emissive[2], 3)
            emissiveTag.addAttr("a", self.emissive[3], 3)
            tag.addChild(emissiveTag)
        # TODO:  Consider if it is safe to skip specular tag if it is equal
        # to (0, 0, 0, *).  I think so.
        specularTag = _XmlTag("specular")
        specularTag.addAttr("r", self.specular[0], 3)
        specularTag.addAttr("g", self.specular[1], 3)
        specularTag.addAttr("b", self.specular[2], 3)
        specularTag.addAttr("a", self.specular[3], 3)
        tag.addChild(specularTag)
        return tag


from Blender.Texture import Types as _bTexTypes
from Blender.Texture import ExtendModes as _bTexExtModes
from Blender.Texture import ImageFlags as _bImgFlags
from Blender.Texture import Flags as _bTexFlags
from Blender.Texture import TexCo as _bTexCo
from Blender.Texture import BlendModes as _bBlendModes
from Blender.Texture import Mappings as _bTexMappings
from Blender.Texture import MapTo as _bTexMapTo
class JmeTexture(object):
    "A Texture corresponding to a single jME Texture"

    REQUIRED_IMGFLAGS = \
        _bImgFlags['MIPMAP'] | _bImgFlags['USEALPHA'] | _bImgFlags['INTERPOL']

    def supported(mtex):
        """Static method that validates the specified Blender MTex.
        MTex is Blender's Material-specific Texture-holder.
        DOES NOT RETURN A MEANINGFUL VALUE.
        Will return upon validation success.
        Otherwise will raise an UnsupportedException with a detail message."""
        
        tex = mtex.tex
        if tex == None:
            raise UnsupportedExcpeption("texture", tex,
                    "MTex has no target Texture")

        # Would like to support those prohibited in this code block.
        if mtex.colfac != 1.0:
            raise UnsupportedException("MTex colfac", mtex.colfac)
        if mtex.size[0] == None or mtex.size[1] == None or mtex.size[2] == None:
            raise UnsupportedException("A null mtex (scale) size dimension")
        # This is a much more general solution than setting "flip".
        if mtex.ofs[0] == None or mtex.ofs[1] == None or mtex.ofs[2] == None:
            raise UnsupportedException("A null mtex offset dimension")
        if JmeTexture.REQUIRED_IMGFLAGS != tex.imageFlags:
            raise UnsupportedException("Tex Image flags", tex.imageFlags,
            "not USEALPHA + MIPMAP + INTERPOL")

        if tex.image == None:
            raise UnsupportedException(
                    "texture image", tex.image, "no image")
        if tex.image.filename == None:
            raise UnsupportedException("texture image file",
                    tex.image.filename, "no image file name")
        if tex.type != _bTexTypes['IMAGE']:
            raise UnsupportedException("Texture Type", tex.type)
        #print "TEX anti: " + str(tex.anti)  Attr missing???
        if tex.crop != (0.0, 0.0, 1.0, 1.0):
            raise UnsupportedException("Tex cropping extents",
                    str(tex.crop))
        # As implement ExtendModes, remove tests from here:
        if (tex.extend != _bTexExtModes['REPEAT']
                and tex.extend != _bTexExtModes['CLIP']
                and tex.extend != _bTexExtModes['EXTEND']):
            raise UnsupportedException("Tex extend mode", tex.extend)
        if tex.brightness != 1.0:
            raise UnsupportedException("Tex brightness", tex.brightness)
        if tex.calcAlpha != 0:
            raise UnsupportedException( "Tex calcAlpha", tex.calcAlpha)
        if len(tex.colorband) != 0:
            raise UnsupportedException("Tex colorband.len",
                    len(tex.colorband))
        if tex.contrast != 1.0:
            raise UnsupportedException("Tex contrast", tex.contrast)
        if tex.filterSize != 1.0:
            raise UnsupportedException("Tex filterSize" +tex.filterSize)
        # Allow PREVIEW_ALPHA, since Blender dev environment setting.
        if tex.flags & _bTexFlags['FLIPBLEND']:
            raise UnsupportedException("Tex flags", 'FLIPBLEND')
        if tex.flags & _bTexFlags['NEGALPHA']:
            raise UnsupportedException("Tex flags", 'NEGALPHA')
        #if tex.flags & _bTexFlags['CHECKER_ODD']:
            #raise UnsupportedException("Tex flags", 'CHECKER_ODD')
            # This is on by default, but the Blender Gui doesn't show
            # checkering on.  ?
        if tex.flags & _bTexFlags['CHECKER_EVEN']:
            raise UnsupportedException("Tex flags", 'CHECKER_EVEN')
        if tex.flags & _bTexFlags['COLORBAND']:
            raise UnsupportedException("Tex flags", 'COLORBAND')
        if tex.flags & _bTexFlags['REPEAT_XMIR']:
            raise UnsupportedException("Tex flags", 'REPEAT_XMIR')
        if tex.flags & _bTexFlags['REPEAT_YMIR']:
            raise UnsupportedException("Tex flags", 'REPEAT_YMIR')
        if tex.repeat[0] != 1:
            raise UnsupportedException("Tex X-Repeat", tex.repeat[0])
        if tex.repeat[1] != 1:
            raise UnsupportedException("Tex Y-Repeat", tex.repeat[1])
        # Map Input
        if mtex.texco != _bTexCo["STICK"] and mtex.texco != _bTexCo["UV"]:
            raise UnsupportedException("Coordinate Mapping type",
                    mtex.texco)
        # Just ignore uvlayer.  We don't care what layer names the user has
        # defined, nor which they set to active.
        if (mtex.blendmode != _bBlendModes['MIX'] # == jME ApplyMode.Decal
                and mtex.blendmode != _bBlendModes['MULTIPLY'] # Modulate
                and mtex.blendmode != _bBlendModes['ADD']): # Add
            raise UnsupportedException("MTex blendmode", mtex.blendmode)
        if mtex.mapping != _bTexMappings['FLAT']:
            raise UnsupportedException("MTex mapping shape", mtex.mapping)
        if mtex.mapto != _bTexMapTo['COL']:
            raise UnsupportedException("MTex mapTo", mtex.mapto)
        if mtex.correctNor:
            raise UnsupportedException("MTex correctNor", mtex.correctNor)
        if round(mtex.dispfac, 3) != .2:
            raise UnsupportedException("MTex surface disp. fac.",
                    mtex.dispfac)
        if mtex.fromOrig:
            raise UnsupportedException("MTex fromOrig", mtex.fromOrig)
        if mtex.neg: raise UnsupportedException("MTex negate", mtex.neg)
        if mtex.norfac != .5:
            raise UnsupportedException("MTex normal affec factor",
                    mtex.norfac)
        if mtex.stencil:
            raise UnsupportedException("MTex stencil", mtex.stencil)
        if mtex.warpfac != 0.0:
            raise UnsupportedException("MTex warpfac", mtex.warpfac)
        if mtex.xproj != 1:
            raise UnsupportedException("MTex xproj", mtex.xproj)
        if mtex.yproj != 2:
            raise UnsupportedException("MTex yproj" + mtex.yproj)
        if mtex.zproj != 3:
            raise UnsupportedException("MTex zproj" + mtex.zproj)

    def idFor(mtex):
        """Static method that validates mtex and returns a unique JmeTexture id
        Input MTex must already have been validated."""

        hashVal = 2 * id(mtex.tex)
        hashVal += 3 * id(mtex.blendmode)
        # Remember that the mtex.tex hash code above encompasses hashes of
        # all of the mtex.tex.* values.  We only need to be concerned about
        # direct and significant mtex attributes here.
        return hashVal

    __slots__ = (
            'written', 'refCount', 'applyMode', 'filepath', 'wrapMode',
            'refid', 'scale', 'translation')
    idFor = staticmethod(idFor)
    supported = staticmethod(supported)

    def __init__(self, mtex, newId):
        "Throws a descriptive UnsupportedException for the obvious reason"
        # TODO:  Look into whether Blender persistence supports saving
        #        image references, so we can share (possibly large) Image
        #        objects instead of loading separate copies from FS for each
        #        JmeTexture.

        object.__init__(self)
        self.written = False   # May write refs after written is True
        self.refCount = 0
        if mtex.blendmode == _bBlendModes['MIX']:
            self.applyMode = "Decal"
        elif mtex.blendmode == _bBlendModes['MULTIPLY']:
            self.applyMode = "Modulate"  # This is the jME default
        elif mtex.blendmode == _bBlendModes['ADD']:
            self.applyMode = "Add"
        else:
            raise Exception("Unexpected blendmode even though pre-validated: "
                    + mtex.blendmode)
        if mtex.tex.extend == _bTexExtModes['REPEAT']:
            self.wrapMode = "Repeat"
        elif mtex.tex.extend == _bTexExtModes['EXTEND']:
            self.wrapMode = "Clamp"
        elif mtex.tex.extend == _bTexExtModes['CLIP']:
            self.wrapMode = "BorderClamp"
            # I haven't got this to reveal the underlaying mat yet, but it's
            # the closes wrap mode we have.  May require the right applyMode.
        else:
            raise Exception("Unexpected extend mode even though pre-validated: "
                    + mtex.tex.extend)
        if (len(mtex.tex.image.filename) > 2
                and mtex.tex.image.filename[0:2] == "//"):
            self.filepath = mtex.tex.image.filename[2:]
        else:
            self.filepath = mtex.tex.image.filename
        if mtex.size[0] == 1. and mtex.size[1] == 1. and mtex.size[2] == 1.:
            self.scale = None
        else:
            self.scale = mtex.size
        if (mtex.ofs[0] == 0. and mtex.ofs[1] == 0. and mtex.ofs[2] == 0.
                and self.scale == None):
            self.translation = None
        else:
            translBase = [mtex.ofs[0], -mtex.ofs[1], mtex.ofs[2]]
            if self.scale == None:
                scalingOffset = [0., 0., 0.]
            else:
                scalingOffset = [.5 - .5 * self.scale[0],
                        .5 + -.5 * self.scale[1],
                        .5 - .5 * self.scale[2]]
            self.translation = [translBase[0] + scalingOffset[0],
                    translBase[1] + scalingOffset[1],
                    translBase[2] + scalingOffset[2]]
        self.refid = newId

    def getXmlEl(self):
        tag = _XmlTag('com.jme.image.Texture2D')
        if self.written:
            tag.addAttr('ref', self.refid)
            return tag
        self.written = True
        if self.refCount > 0: tag.addAttr("reference_ID", self.refid)

        tag.addAttr("apply", self.applyMode)
        tag.addAttr("wrapS", self.wrapMode)
        tag.addAttr("wrapT", self.wrapMode)
        if self.translation != None:
            translTag = _XmlTag(
                    "translation", {"class":"com.jme.math.Vector3f"})
            translTag.addAttr("x", self.translation[0], 6)
            translTag.addAttr("y", self.translation[1], 6)
            translTag.addAttr("z", self.translation[2], 6)
            tag.addChild(translTag)
        if self.scale != None:
            scaleTag = _XmlTag("scale", {"class":"com.jme.math.Vector3f"})
            scaleTag.addAttr("x", self.scale[0], 6)
            scaleTag.addAttr("y", self.scale[1], 6)
            scaleTag.addAttr("z", self.scale[2], 6)
            tag.addChild(scaleTag)
        textureKeyTag = _XmlTag(
                "textureKey", {"class":"com.jme.util.TextureKey"})
        tag.addChild(textureKeyTag)
        textureKeyTag.addAttr("file", self.filepath)
        textureKeyTag.addAttr("protocol", "file")
        return tag


class JmeTextureState(object):
    "A unique list of JmeTextures"

    __slots__ = ('__jmeTextures', 'written', 'refCount')

    def __init__(self, jmeTextures):
        object.__init__(self)
        self.written = False   # May write refs after written is True
        self.__jmeTextures = jmeTextures
        self.refCount = 0

    def cf(self, jmeTextureList):
        if len(self.__jmeTextures) != len(jmeTextureList): return false
        return set(self.__jmeTextures) == set(jmeTextureList)

    def getXmlEl(self):
        tag = _XmlTag('com.jme.scene.state.TextureState',
                {'class':"com.jme.scene.state.lwjgl.LWJGLTextureState"})
        if self.written:
            tag.addAttr('ref', id(self))
            return tag
        self.written = True
        if self.refCount > 0: tag.addAttr("reference_ID", id(self))

        textureGroupingTag = _XmlTag("texture")
        tag.addChild(textureGroupingTag)
        for texture in self.__jmeTextures:
            textureGroupingTag.addChild(texture.getXmlEl())
        textureGroupingTag.addAttr("size", len(self.__jmeTextures))
        return tag

class UpdatableMVert:
    #__slots__ = ('co', 'hide', 'index', 'no', 'sel', 'uvco')
    __slots__ = ('co', 'index', 'no', 'uvco', 'origIndex')
    # For efficiency, cut out the attrs that we will never use.
    # Very important to retain the original vertex's uvco, since these are
    # used when writing sticky uv values for dupped verts.
    # Need to keep track of the original index so that loops after the one
    # which added the duplicate can (1) loop through just the original
    # vertexes, then (2) loop through added vertexes, copying results just
    # derived for the original source vertex.

    def __init__(self, mvert, newIndex, mesh):
        object.__init__(self)
        self.co = mvert.co
        #self.hide = mvert.hide
        self.origIndex = mvert.index
        self.index = newIndex
        self.no = mvert.no
        #self.sel = mvert.sel
        if mesh.vertexUV: self.uvco = mvert.uvco
