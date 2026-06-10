package com.yahya.jdf.registry;

import com.yahya.jdf.JurassicDnaFusion;
import com.yahya.jdf.item.SyringeItem;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Tous les items du mod.
 */
public class ModItems {
    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(JurassicDnaFusion.MODID);

    /**
     * La seringue : l'outil central du mod.
     * Vide  -> clic droit sur une créature = extraire son ADN.
     * Pleine -> maintenir clic droit = s'injecter l'ADN et gagner des capacités.
     */
    public static final DeferredItem<SyringeItem> SYRINGE = ITEMS.registerItem(
            "syringe", SyringeItem::new, new Item.Properties().stacksTo(1));

    /** Ambre brut : contiendra des moustiques préhistoriques (source d'ADN de dino). */
    public static final DeferredItem<Item> AMBER = ITEMS.registerSimpleItem("amber");

    /** L'item-bloc qui permet de poser le bloc de fossile. */
    public static final DeferredItem<BlockItem> FOSSIL_BLOCK_ITEM =
            ITEMS.registerSimpleBlockItem("fossil_block", ModBlocks.FOSSIL_BLOCK);
}
