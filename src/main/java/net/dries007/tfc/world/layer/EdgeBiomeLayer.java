/*
 * Licensed under the EUPL, Version 1.2.
 * You may obtain a copy of the Licence at:
 * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package net.dries007.tfc.world.layer;

import java.util.function.IntPredicate;
import java.util.function.Predicate;

import net.dries007.tfc.world.layer.framework.AdjacentTransformLayer;
import net.dries007.tfc.world.layer.framework.AreaContext;

import static net.dries007.tfc.world.layer.TFCLayerUtil.*;

public enum EdgeBiomeLayer implements AdjacentTransformLayer
{
    INSTANCE;

    @Override
    public int apply(AreaContext context, int north, int east, int south, int west, int center)
    {
        Predicate<IntPredicate> matcher = p -> p.test(north) || p.test(east) || p.test(south) || p.test(west);
        if (center == PLATEAU || center == BADLANDS)
        {
            if (matcher.test(i -> i == LOW_CANYONS || i == LOWLANDS))
            {
                return HILLS;
            }
            else if (matcher.test(i -> i == PLAINS || i == HILLS))
            {
                return ROLLING_HILLS;
            }
        }
        else if (TFCLayerUtil.isMountains(center))
        {
            if (matcher.test(TFCLayerUtil::isLow))
            {
                return ROLLING_HILLS;
            }
        }
        // Inverses of above conditions
        else if (center == LOWLANDS || center == LOW_CANYONS)
        {
            if (matcher.test(i -> i == PLATEAU || i == BADLANDS))
            {
                return HILLS;
            }
            else if (matcher.test(TFCLayerUtil::isMountains))
            {
                return ROLLING_HILLS;
            }
        }
        else if (center == PLAINS || center == HILLS)
        {
            if (matcher.test(i -> i == PLATEAU || i == BADLANDS))
            {
                return HILLS;
            }
            else if (matcher.test(TFCLayerUtil::isMountains))
            {
                return ROLLING_HILLS;
            }
        }
        else if (center == DEEP_OCEAN_TRENCH)
        {
            if (matcher.test(i -> !TFCLayerUtil.isOcean(i)))
            {
                return OCEAN;
            }
        }
        return center;
    }
}