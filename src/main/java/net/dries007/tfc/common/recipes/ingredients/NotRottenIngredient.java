/*
 * Licensed under the EUPL, Version 1.2.
 * You may obtain a copy of the Licence at:
 * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 */

package net.dries007.tfc.common.recipes.ingredients;

import javax.annotation.Nullable;

import com.google.gson.JsonObject;
import net.minecraft.item.ItemStack;
import net.minecraft.item.crafting.Ingredient;
import net.minecraft.network.PacketBuffer;
import net.minecraftforge.common.crafting.CraftingHelper;
import net.minecraftforge.common.crafting.IIngredientSerializer;

import net.dries007.tfc.common.capabilities.food.FoodCapability;
import net.dries007.tfc.util.Helpers;

/**
 * An ingredient which respects non-rotten foods
 */
public class NotRottenIngredient extends DelegateIngredient
{
    protected NotRottenIngredient(Ingredient delegate)
    {
        super(delegate);
    }

    @Override
    public boolean test(@Nullable ItemStack stack)
    {
        return super.test(stack) && stack != null && stack.getCapability(FoodCapability.CAPABILITY).map(cap -> !cap.isRotten()).orElse(true);
    }

    @Override
    public IIngredientSerializer<? extends Ingredient> getSerializer()
    {
        return TFCIngredients.NOT_ROTTEN;
    }

    public static class Serializer implements IIngredientSerializer<NotRottenIngredient>
    {
        @Override
        public NotRottenIngredient parse(PacketBuffer buffer)
        {
            return new NotRottenIngredient(Ingredient.fromNetwork(buffer));
        }

        @Override
        public NotRottenIngredient parse(JsonObject json)
        {
            final Ingredient internal = Ingredient.fromJson(Helpers.getJsonAsAny(json, "ingredient"));
            return new NotRottenIngredient(internal);
        }

        @Override
        public void write(PacketBuffer buffer, NotRottenIngredient ingredient)
        {
            CraftingHelper.write(buffer, ingredient.delegate);
        }
    }
}
