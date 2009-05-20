package com.g3d.input.binding;

//import com.jme.input.MouseInput;

import com.g3d.input.binding.Trigger;


public class MouseAxisTrigger implements Trigger {

    private int axisIndex = -1;
    private boolean negative = false;

    public MouseAxisTrigger(int axis, boolean negative){
        axisIndex = axis;
        this.negative = negative;
    }

    public String getName() {
        String name = "Invalid";
        switch (axisIndex){
            case 0:
                name = "X Axis";
                break;
            case 1:
                name = "Y Axis";
                break;
            case 2:
                name = "Wheel Axis";
                break;
        }

        name += negative ? " Negative" : " Positive";
        return name;
    }

    public float getValue() {
        float value = 0f;
        switch (axisIndex){
            case 0:
//                value = (float) MouseInput.get().getXDelta() / 100f;
                break;
            case 1:
//                value = (float) MouseInput.get().getYDelta() / 100f;
                break;
            case 2:
//                value = MouseInput.get().getWheelDelta() / 100f;
                break;
        }

        if (negative)
            return value >= 0f ? 0f : -value;
        else
            return value <= 0f ? 0f : value;
    }

}
