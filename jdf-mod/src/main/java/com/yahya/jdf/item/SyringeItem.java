package com.yahya.jdf.item;

import java.util.List;

import com.yahya.jdf.registry.ModDataComponents;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

/**
 * La seringue, cœur du gameplay "fusion d'ADN".
 *
 * Cycle d'utilisation :
 *  1. Seringue VIDE + clic droit sur une créature  -> on prélève son ADN
 *     (la créature prend un petit dégât, l'item mémorise son espèce).
 *  2. Seringue PLEINE + maintenir clic droit       -> on S'INJECTE l'ADN
 *     et on gagne des capacités selon l'espèce, puis la seringue se vide.
 *
 * Plus tard, les dinosaures du mod s'ajouteront simplement à la table
 * d'effets dans applyDnaEffects().
 */
public class SyringeItem extends Item {
    /** Durée (en ticks) pendant laquelle il faut maintenir le clic pour s'injecter. */
    private static final int INJECTION_TICKS = 32;
    /** Durée des effets obtenus : 60 secondes (20 ticks = 1 seconde). */
    private static final int EFFECT_DURATION = 20 * 60;

    public SyringeItem(Properties properties) {
        super(properties);
    }

    /** Clic droit sur une créature vivante : extraction d'ADN. */
    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (stack.has(ModDataComponents.DNA_SOURCE.get())) {
            // Déjà pleine : on ne re-prélève pas par-dessus.
            return InteractionResult.PASS;
        }
        if (!player.level().isClientSide) {
            ResourceLocation sourceId = BuiltInRegistries.ENTITY_TYPE.getKey(target.getType());
            stack.set(ModDataComponents.DNA_SOURCE.get(), sourceId);
            // La prise de sang n'est pas indolore...
            target.hurt(player.damageSources().sting(player), 1.0F);
            player.level().playSound(null, target.blockPosition(),
                    SoundEvents.BEE_STING, SoundSource.PLAYERS, 0.8F, 1.4F);
        }
        return InteractionResult.sidedSuccess(player.level().isClientSide);
    }

    /** Clic droit dans le vide : si la seringue est pleine, on commence l'injection. */
    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (stack.has(ModDataComponents.DNA_SOURCE.get())) {
            player.startUsingItem(hand);
            return InteractionResultHolder.consume(stack);
        }
        return InteractionResultHolder.pass(stack);
    }

    /** Appelé quand le joueur a maintenu le clic assez longtemps : l'injection a lieu. */
    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        ResourceLocation sourceId = stack.get(ModDataComponents.DNA_SOURCE.get());
        if (!level.isClientSide && sourceId != null) {
            applyDnaEffects(entity, sourceId);
            // L'injection fait un peu mal, c'est le prix de la science.
            entity.hurt(entity.damageSources().sting(entity), 1.0F);
            stack.remove(ModDataComponents.DNA_SOURCE.get());
            level.playSound(null, entity.blockPosition(),
                    SoundEvents.HONEY_DRINK, SoundSource.PLAYERS, 1.0F, 1.6F);
        }
        return stack;
    }

    /**
     * La table "ADN -> capacités". C'est ici que la magie opère, et c'est ici
     * qu'on ajoutera les dinosaures (raptor -> vitesse + vision nocturne,
     * t-rex -> force, mosasaure -> respiration aquatique, etc.).
     */
    private void applyDnaEffects(LivingEntity entity, ResourceLocation sourceId) {
        switch (sourceId.toString()) {
            case "minecraft:chicken" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, EFFECT_DURATION));
            case "minecraft:rabbit" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.JUMP, EFFECT_DURATION, 1));
            case "minecraft:horse" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, EFFECT_DURATION, 1));
            case "minecraft:cat", "minecraft:ocelot" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, EFFECT_DURATION));
            case "minecraft:turtle", "minecraft:axolotl" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, EFFECT_DURATION));
            case "minecraft:dolphin" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, EFFECT_DURATION));
            case "minecraft:iron_golem" -> {
                entity.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, EFFECT_DURATION));
                entity.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, EFFECT_DURATION));
            }
            case "minecraft:goat" ->
                    entity.addEffect(new MobEffectInstance(MobEffects.JUMP, EFFECT_DURATION, 2));
            // ADN inconnu ou incompatible : le corps n'apprécie pas.
            default ->
                    entity.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 20 * 12));
        }
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return INJECTION_TICKS;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.BOW;
    }

    /** Le tooltip indique ce que contient la seringue. */
    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        ResourceLocation sourceId = stack.get(ModDataComponents.DNA_SOURCE.get());
        if (sourceId != null) {
            EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(sourceId);
            tooltip.add(Component.translatable("tooltip.jdf.dna_source", type.getDescription())
                    .withStyle(ChatFormatting.GREEN));
            tooltip.add(Component.translatable("tooltip.jdf.syringe_inject")
                    .withStyle(ChatFormatting.DARK_GRAY));
        } else {
            tooltip.add(Component.translatable("tooltip.jdf.syringe_empty")
                    .withStyle(ChatFormatting.GRAY));
        }
    }

    /** Petit effet brillant quand la seringue contient de l'ADN. */
    @Override
    public boolean isFoil(ItemStack stack) {
        return stack.has(ModDataComponents.DNA_SOURCE.get());
    }
}
