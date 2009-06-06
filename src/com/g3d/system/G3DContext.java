package com.g3d.system;

import com.g3d.input.JoyInput;
import com.g3d.input.KeyInput;
import com.g3d.input.MouseInput;
import com.g3d.renderer.Renderer;
import javax.naming.Context;

/**
 * Represents a rendering context within the engine.
 */
public interface G3DContext {

    /**
     * The type of context.
     */
    public enum Type {
        /**
         * A display can represent a windowed or a fullscreen-exclusive display.
         * If windowed, the graphics are rendered to a new onscreen surface
         * enclosed in a system defined by the operating system. Implementations
         * are encourged to not use AWT or Swing to create the OpenGL display
         * but rather use native operating system functions to set up a native
         * display with the windowing system.
         */
        Display,
        
        /**
         * 
         */
        Canvas,
        
        /**
         * An <code>OffscreenSurface</code> is a context that is not visible
         * by the user. The application can use the offscreen surface to do
         * General Purpose GPU computations or render a scene into a buffer
         * in order to save it as a screenshot, video or send through a network.
         */
        OffscreenSurface
    }

    /**
     * @return The type of the context.
     */
    public Type getType();

    /**
     * @return True if the user requested to close the context.
     */
    public boolean isCloseRequested();
    
    /**
     * @param settings the display settings to use for the created context. If
     * the context has already been created, then <code>restart()</code> must be called
     * for the changes to be applied.
     */
    public void setSettings(AppSettings settings);

    /**
     * Sets the listener that will recieve events relating to context
     * creation, update, and destroy.
     */
    public void setContextListener(ContextListener listener);

    /**
     * @return The current display settings. Note that they might be 
     * different from the ones set with setDisplaySettings() if the context
     * was restarted or the settings changed internally.
     */
    public AppSettings getSettings();

    /**
     * @return The renderer for this context, or null if not created yet.
     */
    public Renderer getRenderer();

    /**
     * @return Mouse input implementation. May be null if not available.
     */
    public MouseInput getMouseInput();

    /**
     * @return Keyboard input implementation. May be null if not available.
     */
    public KeyInput getKeyInput();

    /**
     * @return Joystick input implementation. May be null if not available.
     */
    public JoyInput getJoyInput();

    /**
     * @return The timer for this context, or null if not created yet.
     */
    public Timer getTimer();

    /**
     * @return True if the context has been created but not yet destroyed.
     */
    public boolean isCreated();

    /**
     * @return True if the context is in focus/visible on the screen.
     * Can be used to reduce resource consumption when the application
     * is not visible on the screen.
     */
    public boolean isActive();

    /**
     * Creates the context and makes it active.
     */
    public void create();

    /**
     * Destroys and then re-creates the context. This should be called after
     * the display settings have been changed.
     *
     * @param updateCamera If true, the current renderer's camera will
     * be resized to match the new resolution in the settings.
     */
    public void restart(boolean updateCamera);

    /**
     * Destroys the context completely, making it inactive.
     */
    public void destroy();

}
