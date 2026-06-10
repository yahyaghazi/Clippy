package com.yahya.jdf.registry;

import java.util.function.Supplier;

import com.yahya.jdf.JurassicDnaFusion;

import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Les "data components" sont la façon moderne (1.20.5+) d'attacher des
 * données à un ItemStack (avant on utilisait du NBT brut).
 *
 * Ici, DNA_SOURCE stocke l'identifiant de la créature dont l'ADN a été
 * prélevé (ex: "minecraft:chicken") directement sur la seringue.
 */
public class ModDataComponents {
    public static final DeferredRegister<DataComponentType<?>> DATA_COMPONENTS =
            DeferredRegister.create(Registries.DATA_COMPONENT_TYPE, JurassicDnaFusion.MODID);

    public static final Supplier<DataComponentType<ResourceLocation>> DNA_SOURCE =
            DATA_COMPONENTS.register("dna_source", () -> DataComponentType.<ResourceLocation>builder()
                    // persistent = sauvegardé sur le disque avec le monde
                    .persistent(ResourceLocation.CODEC)
                    // networkSynchronized = envoyé au client (pour le tooltip)
                    .networkSynchronized(ResourceLocation.STREAM_CODEC)
                    .build());
}
