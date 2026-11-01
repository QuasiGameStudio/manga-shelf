package com.gamezone.darumabash.lwjgl3;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.files.FileHandle;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.freetype.FreeTypeFontGenerator;
import com.badlogic.gdx.graphics.g2d.freetype.FreeTypeFontGenerator.FreeTypeFontParameter;
import com.gamezone.darumabash.Platform;

/**
 * Desktop implementation of {@link Platform}: rasterises the UI typeface from the TTF on startup,
 * which is what the game was written against, and writes screenshots from the GL framebuffer.
 *
 * <p>Baloo 2 ExtraBold is chunky and playful to match the art, but with open counters and a very
 * tall x-height, so the lettering stays readable at the 23 px size the HUD uses. Override with
 * {@code -Dcatch.font=<file in assets/fonts>} to compare faces.
 */
final class DesktopPlatform implements Platform.Impl {

    private static final String DEFAULT_FONT = "Baloo2-ExtraBold.ttf";

    @Override
    public BitmapFont createFont(int size, float border, int shadow, Color text, Color outline) {
        String fontName = System.getProperty("daruma.font", DEFAULT_FONT);
        FileHandle file = Gdx.files.internal("fonts/" + fontName);
        if (!file.exists()) {
            Gdx.app.error("DesktopPlatform",
                    "fonts/" + fontName + " missing - using the font bundled in gdx.jar");
            BitmapFont fallback = new BitmapFont();
            fallback.getData().setScale(size >= 60 ? 4.0f : size >= 26 ? 1.7f : 1.3f);
            return fallback;
        }

        FreeTypeFontGenerator generator = new FreeTypeFontGenerator(file);
        try {
            FreeTypeFontParameter parameter = new FreeTypeFontParameter();
            parameter.size = size;
            parameter.color = new Color(text);
            parameter.borderWidth = border;
            parameter.borderColor = new Color(outline);
            parameter.shadowOffsetX = shadow;
            parameter.shadowOffsetY = shadow;
            parameter.shadowColor = new Color(0f, 0f, 0f, 0.35f);
            parameter.minFilter = Texture.TextureFilter.Linear;
            parameter.magFilter = Texture.TextureFilter.Linear;
            return generator.generateFont(parameter);
        } finally {
            generator.dispose();
        }
    }

    @Override
    public void captureScreenshot(String path) {
        Screenshot.capture(path);
    }
}
