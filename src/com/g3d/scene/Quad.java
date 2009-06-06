package com.g3d.scene;

import com.g3d.scene.VertexBuffer.Type;
import com.g3d.util.BufferUtils;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;

public class Quad extends Mesh {

    public Quad(float width, float height){
        updateGeometry(width, height);
    }

    public Quad(float width, float height, boolean flipCoords){
        updateGeometry(width, height, flipCoords);
    }

    public void updateGeometry(float width, float height){
        updateGeometry(width, height, false);
    }

    public void updateGeometry(float width, float height, boolean flipCoords) {
        setBuffer(Type.Position, 3, new float[]{0,      height, 0,
                                                width,  height, 0,
                                                0,      0,      0,
                                                width,  0,      0});

        if (flipCoords){
            setBuffer(Type.TexCoord, 2, new float[]{0, 0,
                                                    1, 0,
                                                    0, 1,
                                                    1, 1});
        }else{
            setBuffer(Type.TexCoord, 2, new float[]{0, 1,
                                                    1, 1,
                                                    0, 0,
                                                    1, 0});
        }
        setBuffer(Type.Normal, 3, new float[]{0, 0, 1,
                                              0, 0, 1,
                                              0, 0, 1,
                                              0, 0, 1});
        setBuffer(Type.Index, 3, new short[]{0, 1, 2,
                                             1, 3, 2});
    }


}
