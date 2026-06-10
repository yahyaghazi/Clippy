package com.yahya.jdf.registry;

import com.yahya.jdf.JurassicDnaFusion;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Tous les blocs du mod.
 */
public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(JurassicDnaFusion.MODID);

    /**
     * Bloc de fossile : pour l'instant un simple bloc décoratif, mais à terme
     * il génèrera sous terre et se "nettoiera" en fossiles d'espèces précises.
     */
    public static final DeferredBlock<Block> FOSSIL_BLOCK = BLOCKS.registerSimpleBlock(
            "fossil_block",
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.STONE)
                    .strength(1.5f, 6.0f)
                    .requiresCorrectToolForDrops()
                    .sound(SoundType.BONE_BLOCK));
}
