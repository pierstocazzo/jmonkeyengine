/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.jme3.audio;

import com.jme3.asset.AssetManager;
import com.jme3.export.InputCapsule;
import com.jme3.export.JmeExporter;
import com.jme3.export.JmeImporter;
import com.jme3.export.OutputCapsule;
import com.jme3.math.Vector3f;
import com.jme3.scene.Node;
import java.io.IOException;

/**
 *
 * @author normenhansen
 */
public class AudioNode extends Node{
    protected boolean loop = false;
    protected float volume = 1;
    protected float pitch = 1;
    protected float timeOffset = 0;
    protected Filter dryFilter;
    protected AudioKey key;

    protected transient AudioData data = null;
    protected transient Status status = Status.Stopped;
    protected transient int channel = -1;

    protected Vector3f velocity = new Vector3f();
    protected boolean reverbEnabled = true;
    protected float maxDistance = 20; // 20 meters
    protected float refDistance = 10; // 10 meters
    protected Filter reverbFilter;

    private boolean directional = false;
    protected Vector3f direction = new Vector3f(0, 0, 1);
    protected float innerAngle = 360;
    protected float outerAngle = 360;
    private boolean positional = true;

    public enum Status {
        Playing,
        Paused,
        Stopped,
    }

    public AudioNode(){
    }

    public AudioNode(AudioData ad, AudioKey key){
        this();
        setAudioData(ad, key);
    }

    public AudioNode(AssetManager manager, String name, boolean stream){
        this();
        this.key = new AudioKey(name, stream);
        this.data = (AudioData) manager.loadAsset(key);
    }

    public AudioNode(AssetManager manager, String name){
        this(manager, name, false);
    }

    public void setChannel(int channel){
        if (status != Status.Stopped)
            throw new IllegalStateException("Can only set source id when stopped");

        this.channel = channel;
    }

    public int getChannel(){
        return channel;
    }

    public Filter getDryFilter() {
        return dryFilter;
    }

    public void setDryFilter(Filter dryFilter) {
        if (this.dryFilter != null)
            throw new IllegalStateException("Filter already set");

        this.dryFilter = dryFilter;
    }

    public void setAudioData(AudioData ad, AudioKey key){
        if (data != null)
            throw new IllegalStateException("Cannot change data once its set");

        data = ad;
        this.key = key;
    }

    public AudioData getAudioData() {
        return data;
    }

    public Status getStatus(){
        return status;
    }

    public void setStatus(Status status){
        this.status = status;
    }

    public boolean isLooping() {
        return loop;
    }

    public void setLooping(boolean loop) {
        this.loop = loop;
    }

    public float getPitch() {
        return pitch;
    }

    public void setPitch(float pitch) {
        if (pitch < 0.5f || pitch > 2.0f)
            throw new IllegalArgumentException("Pitch must be between 0.5 and 2.0");

        this.pitch = pitch;
    }

    public float getVolume() {
        return volume;
    }

    public void setVolume(float volume) {
        if (volume < 0f)
            throw new IllegalArgumentException("Volume cannot be negative");

        this.volume = volume;
    }

    public float getTimeOffset() {
        return timeOffset;
    }

    public void setTimeOffset(float timeOffset) {
        if (timeOffset < 0f)
            throw new IllegalArgumentException("Time offset cannot be negative");

        this.timeOffset = timeOffset;
    }

//    @Override
//    public AudioNode clone(){
//        try{
//            return (AudioNode) super.clone();
//        }catch (CloneNotSupportedException ex){
//            return null;
//        }
//    }

    /*
     * protected boolean loop = false;
    protected float volume = 1;
    protected float pitch = 1;
    protected float timeOffset = 0;
    protected Filter dryFilter;
    protected AudioKey key;*/

    public void write(JmeExporter ex) throws IOException {
        super.write(ex);
        OutputCapsule oc = ex.getCapsule(this);
        oc.write(key, "key", null);
        oc.write(loop, "looping", false);
        oc.write(volume, "volume", 1);
        oc.write(pitch, "pitch", 1);
        oc.write(timeOffset, "time_offset", 0);
        oc.write(dryFilter, "dry_filter", null);

        oc.write(velocity, "velocity", null);
        oc.write(reverbEnabled, "reverb_enabled", false);
        oc.write(reverbFilter, "reverb_filter", null);
        oc.write(maxDistance, "max_distance", 20);
        oc.write(refDistance, "ref_distance", 10);

        oc.write(directional, "directional", false);
        oc.write(direction, "direction", null);
        oc.write(innerAngle, "inner_angle", 360);
        oc.write(outerAngle, "outer_angle", 360);
    }

    public void read(JmeImporter im) throws IOException {
        super.read(im);
        InputCapsule ic = im.getCapsule(this);
        key =   (AudioKey) ic.readSavable("key", null);
        loop = ic.readBoolean("looping", false);
        volume = ic.readFloat("volume", 1);
        pitch = ic.readFloat("pitch", 1);
        timeOffset = ic.readFloat("time_offset", 0);
        dryFilter = (Filter) ic.readSavable("dry_filter", null);

        velocity = (Vector3f) ic.readSavable("velocity", null);
        reverbEnabled = ic.readBoolean("reverb_enabled", false);
        reverbFilter = (Filter) ic.readSavable("reverb_filter", null);
        maxDistance = ic.readFloat("max_distance", 20);
        refDistance = ic.readFloat("ref_distance", 10);

        directional = ic.readBoolean("directional", false);
        direction = (Vector3f) ic.readSavable("direction", null);
        innerAngle = ic.readFloat("inner_angle", 360);
        outerAngle = ic.readFloat("outer_angle", 360);
    }

    public String toString(){
        String ret = getClass().getSimpleName() +
                     "[status="+status;
        if (volume != 1f)
            ret += ", vol="+volume;
        if (pitch != 1f)
            ret += ", pitch="+pitch;
        return ret + "]";
    }

    /****************/
//    protected Vector3f position = new Vector3f();

    public Vector3f getVelocity() {
        return velocity;
    }

    public void setVelocity(Vector3f velocity) {
        this.velocity.set(velocity);
    }

    public boolean isReverbEnabled() {
        return reverbEnabled;
    }

    public void setReverbEnabled(boolean reverbEnabled) {
        this.reverbEnabled = reverbEnabled;
    }

    public Filter getReverbFilter() {
        return reverbFilter;
    }

    public void setReverbFilter(Filter reverbFilter) {
        if (this.reverbFilter != null)
            throw new IllegalStateException("Filter already set");

        this.reverbFilter = reverbFilter;
    }

    public float getMaxDistance() {
        return maxDistance;
    }

    public void setMaxDistance(float maxDistance) {
        if (maxDistance < 0)
            throw new IllegalArgumentException("Max distance cannot be negative");

        this.maxDistance = maxDistance;
    }

    public float getRefDistance() {
        return refDistance;
    }

    public void setRefDistance(float refDistance) {
        if (refDistance < 0)
            throw new IllegalArgumentException("Reference distance cannot be negative");

        this.refDistance = refDistance;
    }

    /**************************/

    public boolean isDirectional() {
        return directional;
    }

    public void setDirectional(boolean directional) {
        this.directional = directional;
    }


    public Vector3f getDirection() {
        return direction;
    }

    public void setDirection(Vector3f direction) {
        this.direction = direction;
    }

    public float getInnerAngle() {
        return innerAngle;
    }

    public void setInnerAngle(float innerAngle) {
        this.innerAngle = innerAngle;
    }

    public float getOuterAngle() {
        return outerAngle;
    }

    public void setOuterAngle(float outerAngle) {
        this.outerAngle = outerAngle;
    }

    /*********************/
    
    public boolean isPositional() {
        return positional;
    }

    public void setPositional(boolean inHeadspace) {
        this.positional = inHeadspace;
    }

}
