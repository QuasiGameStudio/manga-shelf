package com.gamezone.darumabash.lwjgl3;

import java.nio.ByteBuffer;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.PixmapIO;

/**
 * Grabs the rendered frame straight out of the GL framebuffer and writes it to a PNG.
 *
 * <p>Why this exists: on Windows, capturing an OpenGL window from outside (PrintWindow, a screen
 * grab of a GPU-composited surface) comes back blank white even while the game is drawing happily.
 * Reading the framebuffer from inside the game is the only reliable way to prove what is on
 * screen. Driven by the launcher's {@code --shot=<path>}, so it costs nothing during normal play.
 *
 * <p>Lives in the desktop module because {@link PixmapIO#writePNG} needs a real file system.
 */
final class Screenshot {

    private Screenshot() {
    }

    static void capture(String path) {
        int w = Gdx.graphics.getBackBufferWidth();
        int h = Gdx.graphics.getBackBufferHeight();
        Pixmap raw = Pixmap.createFromFrameBuffer(0, 0, w, h);
        Pixmap flipped = flipY(raw);
        PixmapIO.writePNG(Gdx.files.absolute(path), flipped);
        flipped.dispose();
        raw.dispose();
    }

    /** glReadPixels hands back rows bottom-up; PNG wants them top-down. */
    private static Pixmap flipY(Pixmap source) {
        int w = source.getWidth();
        int h = source.getHeight();
        Pixmap out = new Pixmap(w, h, Pixmap.Format.RGBA8888);
        ByteBuffer in = source.getPixels();
        ByteBuffer dst = out.getPixels();
        int rowBytes = w * 4;
        byte[] row = new byte[rowBytes];
        for (int y = 0; y < h; y++) {
            in.position((h - 1 - y) * rowBytes);
            in.get(row, 0, rowBytes);
            dst.position(y * rowBytes);
            dst.put(row, 0, rowBytes);
        }
        return out;
    }
}
