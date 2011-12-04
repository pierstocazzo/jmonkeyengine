/**
 * evaluate_sceneType.java This file was generated by XMLSpy 2006sp2 Enterprise
 * Edition. YOU SHOULD NOT MODIFY THIS FILE, BECAUSE IT WILL BE OVERWRITTEN WHEN
 * YOU RE-RUN CODE GENERATION. Refer to the XMLSpy Documentation for further
 * details. http://www.altova.com/xmlspy
 */

package com.jmex.model.collada.schema;

import com.jmex.model.collada.types.SchemaNCName;

public class evaluate_sceneType extends com.jmex.model.collada.xml.Node {

    private static final long serialVersionUID = 1L;

    public evaluate_sceneType(evaluate_sceneType node) {
        super(node);
    }

    public evaluate_sceneType(org.w3c.dom.Node node) {
        super(node);
    }

    public evaluate_sceneType(org.w3c.dom.Document doc) {
        super(doc);
    }

    public evaluate_sceneType(com.jmex.model.collada.xml.Document doc,
            String namespaceURI, String prefix, String name) {
        super(doc, namespaceURI, prefix, name);
    }

    public void adjustPrefix() {
        for (org.w3c.dom.Node tmpNode = getDomFirstChild(Attribute, null,
                "name"); tmpNode != null; tmpNode = getDomNextChild(Attribute,
                null, "name", tmpNode)) {
            internalAdjustPrefix(tmpNode, false);
        }
        for (org.w3c.dom.Node tmpNode = getDomFirstChild(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render"); tmpNode != null; tmpNode = getDomNextChild(
                Element, "http://www.collada.org/2005/11/COLLADASchema",
                "render", tmpNode)) {
            internalAdjustPrefix(tmpNode, true);
            new renderType(tmpNode).adjustPrefix();
        }
    }

    public static int getnameMinCount() {
        return 0;
    }

    public static int getnameMaxCount() {
        return 1;
    }

    public int getnameCount() {
        return getDomChildCount(Attribute, null, "name");
    }

    public boolean hasname() {
        return hasDomChild(Attribute, null, "name");
    }

    public SchemaNCName newname() {
        return new SchemaNCName();
    }

    public SchemaNCName getnameAt(int index) throws Exception {
        return new SchemaNCName(getDomNodeValue(dereference(getDomChildAt(
                Attribute, null, "name", index))));
    }

    public org.w3c.dom.Node getStartingnameCursor() throws Exception {
        return getDomFirstChild(Attribute, null, "name");
    }

    public org.w3c.dom.Node getAdvancednameCursor(org.w3c.dom.Node curNode)
            throws Exception {
        return getDomNextChild(Attribute, null, "name", curNode);
    }

    public SchemaNCName getnameValueAtCursor(org.w3c.dom.Node curNode)
            throws Exception {
        if (curNode == null)
            throw new com.jmex.model.collada.xml.XmlException("Out of range");
        else
            return new SchemaNCName(getDomNodeValue(dereference(curNode)));
    }

    public SchemaNCName getname() throws Exception {
        return getnameAt(0);
    }

    public void removenameAt(int index) {
        removeDomChildAt(Attribute, null, "name", index);
    }

    public void removename() {
        while (hasname())
            removenameAt(0);
    }

    public void addname(SchemaNCName value) {
        if (value.isNull() == false) {
            appendDomChild(Attribute, null, "name", value.toString());
        }
    }

    public void addname(String value) throws Exception {
        addname(new SchemaNCName(value));
    }

    public void insertnameAt(SchemaNCName value, int index) {
        insertDomChildAt(Attribute, null, "name", index, value.toString());
    }

    public void insertnameAt(String value, int index) throws Exception {
        insertnameAt(new SchemaNCName(value), index);
    }

    public void replacenameAt(SchemaNCName value, int index) {
        replaceDomChildAt(Attribute, null, "name", index, value.toString());
    }

    public void replacenameAt(String value, int index) throws Exception {
        replacenameAt(new SchemaNCName(value), index);
    }

    public static int getrenderMinCount() {
        return 1;
    }

    public static int getrenderMaxCount() {
        return Integer.MAX_VALUE;
    }

    public int getrenderCount() {
        return getDomChildCount(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render");
    }

    public boolean hasrender() {
        return hasDomChild(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render");
    }

    public renderType newrender() {
        return new renderType(domNode.getOwnerDocument().createElementNS(
                "http://www.collada.org/2005/11/COLLADASchema", "render"));
    }

    public renderType getrenderAt(int index) throws Exception {
        return new renderType(
                dereference(getDomChildAt(Element,
                        "http://www.collada.org/2005/11/COLLADASchema",
                        "render", index)));
    }

    public org.w3c.dom.Node getStartingrenderCursor() throws Exception {
        return getDomFirstChild(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render");
    }

    public org.w3c.dom.Node getAdvancedrenderCursor(org.w3c.dom.Node curNode)
            throws Exception {
        return getDomNextChild(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render",
                curNode);
    }

    public renderType getrenderValueAtCursor(org.w3c.dom.Node curNode)
            throws Exception {
        if (curNode == null)
            throw new com.jmex.model.collada.xml.XmlException("Out of range");
        else
            return new renderType(dereference(curNode));
    }

    public renderType getrender() throws Exception {
        return getrenderAt(0);
    }

    public void removerenderAt(int index) {
        removeDomChildAt(Element,
                "http://www.collada.org/2005/11/COLLADASchema", "render", index);
    }

    public void removerender() {
        while (hasrender())
            removerenderAt(0);
    }

    public void addrender(renderType value) {
        appendDomElement("http://www.collada.org/2005/11/COLLADASchema",
                "render", value);
    }

    public void insertrenderAt(renderType value, int index) {
        insertDomElementAt("http://www.collada.org/2005/11/COLLADASchema",
                "render", index, value);
    }

    public void replacerenderAt(renderType value, int index) {
        replaceDomElementAt("http://www.collada.org/2005/11/COLLADASchema",
                "render", index, value);
    }

    private org.w3c.dom.Node dereference(org.w3c.dom.Node node) {
        return node;
    }
}