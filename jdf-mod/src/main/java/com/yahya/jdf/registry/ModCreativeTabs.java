package com.yahya.jdf.registry;

import com.yahya.jdf.JurassicDnaFusion;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * L'onglet "Jurassic DNA Fusion" dans l'inventaire créatif.
 */
public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, JurassicDnaFusion.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> JDF_TAB =
            CREATIVE_MODE_TABS.register("jdf_tab", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.jdf"))
                    .withTabsBefore(CreativeModeTabs.COMBAT)
                    .icon(() -> ModItems.SYRINGE.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ModItems.SYRINGE.get());
                        output.accept(ModItems.AMBER.get());
                        output.accept(ModItems.FOSSIL_BLOCK_ITEM.get());
                    })
                    .build());
}
