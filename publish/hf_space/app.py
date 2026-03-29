"""Thin Hugging Face Space client backed by the shared SpectralBio core."""

from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import spectralbio.demo.score_variant as demo_contract


def _render_result(gene: str, position: int, mutant_aa: str) -> tuple[str, dict]:
    payload = demo_contract.score_variant_contract(gene, int(position) - 1, mutant_aa)
    request = payload["request"]
    result = payload["result"]
    context = payload["benchmark_context"]
    metrics = payload["official_metrics"]
    is_primary_benchmark = context["benchmark_role"] == demo_contract.PRIMARY_BENCHMARK_ROLE
    if is_primary_benchmark:
        percentile_line = (
            "Combined percentile vs TP53 canonical benchmark: "
            f"{result['reference_calibration']['combined_percentile']:.2f}"
        )
        benchmark_metric_lines = [
            "",
            f"Primary benchmark context | Official TP53 canonical AUC: {metrics['canonical']['auc_best_pair']:.4f}",
            "Secondary bounded transfer context remains available in the raw payload only.",
        ]
    else:
        percentile_line = (
            "Combined percentile calibrated against TP53 canonical benchmark "
            f"for secondary transfer interpretation: {result['reference_calibration']['combined_percentile']:.2f}"
        )
        benchmark_metric_lines = [
            "",
            f"Primary calibration reference | Official TP53 canonical AUC: {metrics['canonical']['auc_best_pair']:.4f}",
            (
                "Secondary bounded transfer reference | Official BRCA1 subset AUC: "
                f"{metrics['transfer']['ll_proper_auc']:.4f}"
            ),
        ]
    summary = [
        f"Contract: {payload['contract_version']}",
        f"Gene: {request['gene']}",
        f"Variant: {result['protein_variant']}",
        f"Benchmark role: {context['benchmark_role']}",
        f"Classification: {result['classification']['label']}",
        percentile_line,
        f"FrobDist: {result['frob_dist']:.6f}",
        f"LL Proper: {result['ll_proper']:.6f}",
        f"TraceRatio: {result['trace_ratio']:.6f}",
        f"Benchmark annotation: {context['benchmark_annotation']}",
        f"Scope note: {context['scope_note']}",
        f"Preset story: {context['preset']['ui_story']}",
        *benchmark_metric_lines,
    ]
    return "\n".join(summary), payload


def _load_preset(preset_name: str) -> tuple[str, int, str]:
    return demo_contract.load_preset_inputs(preset_name)


with gr.Blocks(title="SpectralBio Demo") as demo:
    gr.Markdown(
        "\n".join(
            [
                "# SpectralBio",
                "",
                "**Artifact role:** research reproducibility artifact",
                "",
                "**Primary benchmark:** TP53 canonical executable benchmark",
                "",
                "**Secondary benchmark:** bounded transfer on a fixed BRCA1 subset (N=100)",
                "",
                "**Transfer framing:** secondary transfer evaluation without retraining",
                "",
                "**Adaptation note:** adaptation recipe only",
                "",
                "This Space renders shared-core outputs only and keeps TP53 presets as the default workflow.",
            ]
        )
    )

    with gr.Row():
        preset = gr.Dropdown(
            list(demo_contract.PRESET_NAMES),
            label="Preset-first workflow",
            value=demo_contract.DEFAULT_PRESET_NAME,
        )
        load_preset = gr.Button("Use preset", variant="secondary")

    gr.Markdown(
        "TP53 presets stay first. BRCA1 presets remain clearly secondary bounded transfer examples."
    )

    with gr.Accordion("Advanced manual scoring", open=False):
        with gr.Row():
            gene = gr.Dropdown(
                choices=list(demo_contract.GENE_CHOICES),
                label="Manual gene selection",
                value="TP53",
                info="TP53 is the primary canonical path; BRCA1 is secondary bounded transfer evidence.",
            )
            position = gr.Number(label="Position (1-indexed)", value=175, precision=0)
            mutant_aa = gr.Dropdown(demo_contract.AA_LIST, label="Mutant amino acid", value="H")

    run_button = gr.Button("Score variant", variant="primary")
    summary_output = gr.Textbox(label="Rendered summary", lines=14)
    json_output = gr.JSON(label="Shared contract payload")

    load_preset.click(_load_preset, inputs=[preset], outputs=[gene, position, mutant_aa])
    run_button.click(
        _render_result,
        inputs=[gene, position, mutant_aa],
        outputs=[summary_output, json_output],
        api_name="/score_variant",
    )


if __name__ == "__main__":
    demo.launch()
