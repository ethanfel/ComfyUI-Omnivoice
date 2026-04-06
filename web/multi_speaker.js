import { app } from "../../scripts/app.js";

const MAX_SPEAKERS = 8;

app.registerExtension({
    name: "OmniVoice.MultiSpeaker",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "OmniVoiceSpeakers") return;

        /**
         * Ensure the node has exactly `count` speaker_N inputs.
         * Safe to call multiple times with the same count (idempotent).
         */
        function syncSpeakerInputs(node, count) {
            count = Math.max(2, Math.min(MAX_SPEAKERS, Math.floor(count)));

            // Add any missing slots
            for (let i = 1; i <= count; i++) {
                const name = `speaker_${i}`;
                if (!node.inputs?.find(inp => inp.name === name)) {
                    node.addInput(name, "OMNIVOICE_SPEAKER");
                }
            }

            // Remove excess slots (high → low so indices stay valid)
            for (let i = MAX_SPEAKERS; i > count; i--) {
                const name = `speaker_${i}`;
                const idx = node.inputs?.findIndex(inp => inp.name === name) ?? -1;
                if (idx === -1) continue;
                // Sever any connected link before removing the slot
                const linkId = node.inputs[idx].link;
                if (linkId != null) node.graph?.removeLink(linkId);
                node.removeInput(idx);
            }

            node.setDirtyCanvas(true, true);
        }

        /**
         * Attach the num_speakers widget callback once per node instance.
         * Guarded by a flag so configure() can call it safely on reload.
         */
        function attachCallback(node) {
            if (node._omnivoiceCbAttached) return;
            const w = node.widgets?.find(w => w.name === "num_speakers");
            if (!w) return;
            node._omnivoiceCbAttached = true;
            w.callback = (value) => syncSpeakerInputs(node, value);
        }

        // --- Fresh node creation ---
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);
            attachCallback(this);
            const w = this.widgets?.find(w => w.name === "num_speakers");
            if (w) syncSpeakerInputs(this, w.value);
        };

        // --- Workflow load: called by LiteGraph after widget values are restored ---
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (data) {
            onConfigure?.apply(this, arguments);
            attachCallback(this);
            const w = this.widgets?.find(w => w.name === "num_speakers");
            if (w) syncSpeakerInputs(this, w.value);
        };
    },
});
