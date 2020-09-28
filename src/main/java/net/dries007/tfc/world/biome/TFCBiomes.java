/*
 * Work under Copyright. Licensed under the EUPL.
 * See the project README.md and LICENSE.txt for more information.
 */

package net.dries007.tfc.world.biome;

import java.util.*;
import java.util.function.LongFunction;

import javax.annotation.Nullable;

import net.minecraft.util.RegistryKey;
import net.minecraft.util.ResourceLocation;
import net.minecraft.util.registry.Registry;
import net.minecraft.world.IBiomeReader;
import net.minecraft.world.IWorld;
import net.minecraft.world.IWorldReader;
import net.minecraft.world.biome.Biome;
import net.minecraft.world.biome.BiomeMaker;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;

import net.dries007.tfc.util.collections.FiniteLinkedHashMap;
import net.dries007.tfc.world.noise.INoise2D;

import static net.dries007.tfc.TerraFirmaCraft.MOD_ID;

public final class TFCBiomes
{
    public static final DeferredRegister<Biome> BIOMES = DeferredRegister.create(ForgeRegistries.BIOMES, MOD_ID);

    private static final List<RegistryKey<Biome>> DEFAULT_BIOME_KEYS = new ArrayList<>();
    private static final List<BiomeVariants> VARIANTS = new ArrayList<>();
    private static final Map<RegistryKey<Biome>, BiomeExtension> EXTENSIONS = new HashMap<>(); // All extensions, indexed by registry key for quick access
    private static final Map<Biome, BiomeExtension> CACHED_EXTENSIONS = new FiniteLinkedHashMap<>(128); // Faster route from biome -> extension

    // Aquatic biomes
    public static final BiomeVariants OCEAN = register("ocean", seed -> BiomeNoise.ocean(seed, -24, -6), BiomeVariants.LargeGroup.OCEAN); // Ocean biome found near continents.
    public static final BiomeVariants DEEP_OCEAN = register("deep_ocean", seed -> BiomeNoise.ocean(seed, -36, -10), BiomeVariants.LargeGroup.OCEAN); // Deep ocean biome covering most all oceans.

    // Low biomes
    public static final BiomeVariants PLAINS = register("plains", seed -> BiomeNoise.simple(seed, 4, 10)); // Very flat, slightly above sea level.
    public static final BiomeVariants HILLS = register("hills", seed -> BiomeNoise.simple(seed, -5, 16)); // Small hills, slightly above sea level.
    public static final BiomeVariants LOWLANDS = register("lowlands", BiomeNoise::lowlands); // Flat, swamp-like, lots of shallow pools below sea level.
    public static final BiomeVariants LOW_CANYONS = register("low_canyons", seed -> BiomeNoise.canyons(seed, -5, 15)); // Sharp, small hills, with lots of water / snaking winding rivers.

    // Mid biomes
    public static final BiomeVariants ROLLING_HILLS = register("rolling_hills", seed -> BiomeNoise.simple(seed, -5, 28)); // Higher hills, above sea level. Some larger / steeper hills.
    public static final BiomeVariants BADLANDS = register("badlands", BiomeNoise::badlands); // Very high flat area with steep relief carving, similar to vanilla mesas.
    public static final BiomeVariants PLATEAU = register("plateau", seed -> BiomeNoise.simple(seed, 20, 30)); // Very high area, very flat top.
    public static final BiomeVariants OLD_MOUNTAINS = register("old_mountains", seed -> BiomeNoise.mountains(seed, 16, 40)); // Rounded top mountains, very large hills.

    // High biomes
    public static final BiomeVariants MOUNTAINS = register("mountains", seed -> BiomeNoise.mountains(seed, 10, 70)); // High, picturesque mountains. Pointed peaks, low valleys well above sea level.
    public static final BiomeVariants FLOODED_MOUNTAINS = register("flooded_mountains", seed -> BiomeNoise.mountains(seed, -16, 60)); // Mountains with high areas, and low, below sea level valleys. Water is salt water here.
    public static final BiomeVariants CANYONS = register("canyons", seed -> BiomeNoise.canyons(seed, -7, 26)); // Medium height with snake like ridges, often slightly below sea level

    // Shores
    public static final BiomeVariants SHORE = register("shore", BiomeNoise::shore, BiomeVariants.LargeGroup.OCEAN); // Standard shore biome with a sandy beach

    // Technical biomes
    public static final BiomeVariants LAKE = register("lake", BiomeNoise::lake, BiomeVariants.LargeGroup.LAKE); // Biome for freshwater ocean areas / landlocked oceans
    public static final BiomeVariants RIVER = register("river", seed -> BiomeNoise.simple(seed, -6, -1), BiomeVariants.LargeGroup.RIVER, BiomeVariants.SmallGroup.RIVER); // Biome for river channels

    public static BiomeExtension getExtensionOrThrow(IWorld world, Biome biome)
    {
        BiomeExtension extension = getExtension(world, biome);
        if (extension == null)
        {
            throw new IllegalStateException("Biome missing a required extension!");
        }
        return extension;
    }

    @Nullable
    public static BiomeExtension getExtension(IBiomeReader world, Biome biome)
    {
        // First query the cache, it is fast
        BiomeExtension extension = CACHED_EXTENSIONS.get(biome);
        if (extension == BiomeExtension.EMPTY)
        {
            // No match for this biome - this exists as a cache miss marker
            return null;
        }
        else if (extension != null)
        {
            // Cache hit
            return extension;
        }
        else
        {
            Registry<Biome> registry = world.registryAccess().registryOrThrow(Registry.BIOME_REGISTRY);
            BiomeExtension lookupExtension = registry.getResourceKey(biome).map(EXTENSIONS::get).orElse(null);
            if (lookupExtension != null)
            {
                // Save the extension and biome to the cache
                CACHED_EXTENSIONS.put(biome, lookupExtension);
                return lookupExtension;
            }
            else
            {
                // Mark this as a cache miss with the empty extension
                CACHED_EXTENSIONS.put(biome, BiomeExtension.EMPTY);
                return null;
            }
        }
    }

    public static List<RegistryKey<Biome>> getAllKeys()
    {
        return DEFAULT_BIOME_KEYS;
    }

    public static List<BiomeVariants> getVariants()
    {
        return VARIANTS;
    }

    private static BiomeVariants register(String baseName, LongFunction<INoise2D> noiseFactory)
    {
        return register(baseName, noiseFactory, BiomeVariants.LargeGroup.LAND, BiomeVariants.SmallGroup.BODY);
    }

    private static BiomeVariants register(String baseName, LongFunction<INoise2D> noiseFactory, BiomeVariants.LargeGroup largeGroup)
    {
        return register(baseName, noiseFactory, largeGroup, BiomeVariants.SmallGroup.BODY);
    }

    /**
     * Registers all variants corresponding to a biome super type
     */
    private static BiomeVariants register(String baseName, LongFunction<INoise2D> noiseFactory, BiomeVariants.LargeGroup largeGroup, BiomeVariants.SmallGroup smallGroup)
    {
        BiomeVariants variants = new BiomeVariants(noiseFactory, smallGroup, largeGroup);
        VARIANTS.add(variants);
        for (BiomeTemperature temp : BiomeTemperature.values())
        {
            for (BiomeRainfall rain : BiomeRainfall.values())
            {
                String name = baseName + "_" + temp.name().toLowerCase() + "_" + rain.name().toLowerCase();
                ResourceLocation id = new ResourceLocation(MOD_ID, name);
                RegistryKey<Biome> key = RegistryKey.create(Registry.BIOME_REGISTRY, id);
                BiomeExtension extension = new BiomeExtension(key, temp, rain, variants);

                EXTENSIONS.put(key, extension);
                DEFAULT_BIOME_KEYS.add(key);
                TFCBiomes.BIOMES.register(name, BiomeMaker::theVoidBiome);

                variants.put(temp, rain, extension);
            }
        }
        return variants;
    }
}