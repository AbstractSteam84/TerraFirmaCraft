/*
 * Licensed under the EUPL, Version 1.2.
 * You may obtain a copy of the Licence at:
 * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package net.dries007.tfc.world.noise;

import net.minecraft.util.math.MathHelper;

import net.dries007.tfc.util.function.FloatUnaryFunction;

/**
 * Wrapper for a 2D noise layer
 */
@FunctionalInterface
public interface Noise2D
{
    float noise(float x, float z);

    /**
     * @param octaves The number of octaves
     */
    default Noise2D octaves(int octaves)
    {
        final float[] frequency = new float[octaves];
        final float[] amplitude = new float[octaves];
        for (int i = 0; i < octaves; i++)
        {
            frequency[i] = 1 << i;
            amplitude[i] = (float) Math.pow(0.5f, octaves - i);
        }
        return (x, y) -> {
            float value = 0;
            for (int i = 0; i < octaves; i++)
            {
                value += Noise2D.this.noise(x / frequency[i], y / frequency[i]) * amplitude[i];
            }
            return value;
        };
    }

    /**
     * Creates ridged noise using absolute value
     *
     * @return a new noise function
     */
    default Noise2D ridged()
    {
        return (x, y) -> {
            float value = Noise2D.this.noise(x, y);
            value = value < 0 ? -value : value;
            return 1f - 2f * value;
        };
    }

    /**
     * Takes the absolute value of a noise function. Does not scale the result
     *
     * @return a new noise function
     */
    default Noise2D abs()
    {
        return (x, y) -> Math.abs(Noise2D.this.noise(x, y));
    }

    /**
     * Creates "terraces" by taking the nearest level and rounding
     * Input must be in range [-1, 1]
     *
     * @param levels The number of levels to round to
     * @return a new noise function
     */
    default Noise2D terraces(int levels)
    {
        return (x, y) -> {
            float value = 0.5f * Noise2D.this.noise(x, y) + 0.5f;
            float rounded = (int) (value * levels); // In range [0, levels)
            return (rounded * 2f) / levels - 1f;
        };
    }

    /**
     * Spreads out the noise via the input parameters
     *
     * @param scaleFactor The scale for the input params
     * @return a new noise function
     */
    default Noise2D spread(float scaleFactor)
    {
        return (x, y) -> Noise2D.this.noise(x * scaleFactor, y * scaleFactor);
    }

    default Noise2D scaled(float min, float max)
    {
        return scaled(-1, 1, min, max);
    }

    /**
     * Re-scales the output of the noise to a new range
     *
     * @param oldMin the old minimum value (typically -1)
     * @param oldMax the old maximum value (typically 1)
     * @param min    the new minimum value
     * @param max    the new maximum value
     * @return a new noise function
     */
    default Noise2D scaled(float oldMin, float oldMax, float min, float max)
    {
        final float scale = (max - min) / (oldMax - oldMin);
        final float shift = min - oldMin * scale;
        return (x, y) -> Noise2D.this.noise(x, y) * scale + shift;
    }

    default Noise2D warped(OpenSimplex2D warp)
    {
        warp.fnl.SetDomainWarpType(FastNoiseLite.DomainWarpType.OpenSimplex2);
        warp.fnl.SetFractalType(FastNoiseLite.FractalType.DomainWarpIndependent);
        warp.fnl.SetDomainWarpAmp(warp.getAmplitude() * 2);
        final FastNoiseLite.Vector2 cursor = new FastNoiseLite.Vector2(0, 0);
        return (x, z) -> {
            cursor.x = x;
            cursor.y = z;
            warp.fnl.DomainWarp(cursor);
            return Noise2D.this.noise(cursor.x, cursor.y);
        };
    }

    /**
     * Creates flattened noise by cutting off values above or below a threshold
     *
     * @param min the minimum noise value
     * @param max the maximum noise value
     * @return a new noise function
     */
    default Noise2D flattened(float min, float max)
    {
        return (x, y) -> MathHelper.clamp(Noise2D.this.noise(x, y), min, max);
    }

    default Noise2D add(Noise2D other)
    {
        return (x, y) -> Noise2D.this.noise(x, y) + other.noise(x, y);
    }

    default Noise2D map(FloatUnaryFunction mappingFunction)
    {
        return (x, y) -> mappingFunction.applyAsFloat(Noise2D.this.noise(x, y));
    }
}