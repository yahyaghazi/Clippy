package com.yahya.jdf;

import org.slf4j.Logger;

import com.mojang.logging.LogUtils;
import com.yahya.jdf.registry.ModBlocks;
import com.yahya.jdf.registry.ModCreativeTabs;
import com.yahya.jdf.registry.ModDataComponents;
import com.yahya.jdf.registry.ModItems;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

/**
 * Jurassic DNA Fusion — classe principale du mod.
 *
 * C'est le point d'entrée : NeoForge instancie cette classe au chargement
 * du jeu, et on en profite pour enregistrer tout notre contenu
 * (items, blocs, onglet créatif, data components).
 */
@Mod(JurassicDnaFusion.MODID)
public class JurassicDnaFusion {
    /** L'identifiant unique du mod. Doit correspondre à mod_id dans gradle.properties. */
    public static final String MODID = "jdf";

    public static final Logger LOGGER = LogUtils.getLogger();

    public JurassicDnaFusion(IEventBus modEventBus, ModContainer modContainer) {
        // L'ordre compte un peu : les items de type "BlockItem" référencent des
        // blocs, donc on enregistre les blocs avant les items.
        ModDataComponents.DATA_COMPONENTS.register(modEventBus);
        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modEventBus);

        LOGGER.info("Jurassic DNA Fusion chargé — la vie trouve toujours un chemin.");
    }
}
