/*
 * Copyright (c) 2003-2004, jMonkeyEngine - Mojo Monkey Coding
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * Neither the name of the Mojo Monkey Coding, jME, jMonkey Engine, nor the
 * names of its contributors may be used to endorse or promote products derived
 * from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 */
package com.jme.input;

import com.jme.util.JmeType;


/**
 * <code>MouseButtonStateType</code>
 * @author Gregg Patton
 * @version $Id: MouseButtonStateType.java,v 1.2 2004-04-22 22:26:30 renanse Exp $
 */
public class MouseButtonStateType extends JmeType {

    public final static MouseButtonStateType MOUSE_BUTTON_NONE = new MouseButtonStateType ("MOUSE_BUTTON_NONE");
    public final static MouseButtonStateType MOUSE_BUTTON_1 = new MouseButtonStateType ("MOUSE_BUTTON_1");
    public final static MouseButtonStateType MOUSE_BUTTON_2 = new MouseButtonStateType ("MOUSE_BUTTON_2");
    public final static MouseButtonStateType MOUSE_BUTTON_3 = new MouseButtonStateType ("MOUSE_BUTTON_3");

    public final static MouseButtonStateType MOUSE_BUTTON_1_2 = new MouseButtonStateType ("MOUSE_BUTTON_1_2");
    public final static MouseButtonStateType MOUSE_BUTTON_1_3 = new MouseButtonStateType ("MOUSE_BUTTON_1_3");
    public final static MouseButtonStateType MOUSE_BUTTON_2_3 = new MouseButtonStateType ("MOUSE_BUTTON_2_3");

    public final static MouseButtonStateType MOUSE_BUTTON_1_2_3 = new MouseButtonStateType ("MOUSE_BUTTON_1_2_3");

    public MouseButtonStateType(String name) {
        super(name);
    }

    public JmeType getType(String name) {
        JmeType type = null;

        if (MOUSE_BUTTON_NONE.name.equals(name)) {
            type = MOUSE_BUTTON_NONE;
        } else if (MOUSE_BUTTON_1.name.equals(name)) {
            type = MOUSE_BUTTON_1;
        } else if (MOUSE_BUTTON_2.name.equals(name)) {
            type = MOUSE_BUTTON_2;
        } else if (MOUSE_BUTTON_3.name.equals(name)) {
            type = MOUSE_BUTTON_3;
        } else if (MOUSE_BUTTON_1_2.name.equals(name)) {
            type = MOUSE_BUTTON_1_2;
        } else if (MOUSE_BUTTON_1_3.name.equals(name)) {
            type = MOUSE_BUTTON_1_3;
        } else if (MOUSE_BUTTON_2_3.name.equals(name)) {
            type = MOUSE_BUTTON_2_3;
        } else if (MOUSE_BUTTON_1_2_3.name.equals(name)) {
            type = MOUSE_BUTTON_1_2_3;
        }

        return type;
    }

}
