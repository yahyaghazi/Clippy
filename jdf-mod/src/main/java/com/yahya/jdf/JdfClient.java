package com.yahya.jdf;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

/**
 * Point d'entrée côté client uniquement (rendu, écrans, modèles...).
 * Cette classe n'est jamais chargée sur un serveur dédié.
 *
 * Pour l'instant elle est vide, mais c'est ici qu'on enregistrera plus tard
 * les rendus des dinosaures et les effets visuels de transformation du joueur.
 */
@Mod(value = JurassicDnaFusion.MODID, dist = Dist.CLIENT)
public class JdfClient {
    public JdfClient(ModContainer container) {
    }
}
