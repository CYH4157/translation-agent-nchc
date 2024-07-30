import os
import re
from glob import glob

import gradio as gr
from process import (
    diff_texts,
    extract_docx,
    extract_pdf,
    extract_text,
    model_load,
    translator,
    translator_sec,
)


def huanik(
    endpoint: str,
    base: str,
    model: str,
    api_key: str,
    choice: str,
    endpoint2: str,
    base2: str,
    model2: str,
    api_key2: str,
    source_lang: str,
    target_lang: str,
    source_text: str,
    country: str,
    max_tokens: int,
    temperature: int,
    rpm: int,
):
    if not source_text or source_lang == target_lang:
        raise gr.Error(
            "Please check that the content or options are entered correctly."
        )

    try:
        model_load(endpoint, base, model, api_key, temperature, rpm)
    except Exception as e:
        raise gr.Error(f"An unexpected error occurred: {e}") from e

    source_text = re.sub(r"(?m)^\s*$\n?", "", source_text)

    if choice:
        init_translation, reflect_translation, final_translation = (
            translator_sec(
                endpoint2=endpoint2,
                base2=base2,
                model2=model2,
                api_key2=api_key2,
                source_lang=source_lang,
                target_lang=target_lang,
                source_text=source_text,
                country=country,
                max_tokens=max_tokens,
            )
        )

    else:
        init_translation, reflect_translation, final_translation = translator(
            source_lang=source_lang,
            target_lang=target_lang,
            source_text=source_text,
            country=country,
            max_tokens=max_tokens,
        )

    final_diff = gr.HighlightedText(
        diff_texts(init_translation, final_translation),
        label="Diff translation",
        combine_adjacent=True,
        show_legend=True,
        visible=True,
        color_map={"removed": "red", "added": "green"},
    )

    return init_translation, reflect_translation, final_translation, final_diff


def update_model(endpoint):
    endpoint_model_map = {
        "Groq": "llama3-70b-8192",
        "OpenAI": "gpt-4o",
        "TogetherAI": "Qwen/Qwen2-72B-Instruct",
        "Ollama": "llama3",
        "CUSTOM": "taide-llama2-70b",
    }
    if endpoint == "CUSTOM":
        base = gr.update(visible=True)
    else:
        base = gr.update(visible=False)
    return gr.update(value=endpoint_model_map[endpoint]), base


def read_doc(path):
    file_type = path.split(".")[-1]
    print(file_type)
    if file_type in ["pdf", "txt", "py", "docx", "json", "cpp", "md"]:
        if file_type.endswith("pdf"):
            content = extract_pdf(path)
        elif file_type.endswith("docx"):
            content = extract_docx(path)
        else:
            content = extract_text(path)
        return re.sub(r"(?m)^\s*$\n?", "", content)
    else:
        raise gr.Error("Oops, unsupported files.")


def enable_sec(choice):
    if choice:
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


def update_menu(visible):
    return not visible, gr.update(visible=not visible)


def export_txt(strings):
    if strings:
        os.makedirs("outputs", exist_ok=True)
        base_count = len(glob(os.path.join("outputs", "*.txt")))
        file_path = os.path.join("outputs", f"{base_count:06d}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(strings)
        return gr.update(value=file_path, visible=True)
    else:
        return gr.update(visible=False)


def switch(source_lang, source_text, target_lang, output_final):
    if output_final:
        return (
            gr.update(value=target_lang),
            gr.update(value=output_final),
            gr.update(value=source_lang),
            gr.update(value=source_text),
        )
    else:
        return (
            gr.update(value=target_lang),
            gr.update(value=source_text),
            gr.update(value=source_lang),
            gr.update(value=""),
        )


def close_btn_show():
    return gr.update(visible=False), gr.update(visible=True)


def close_btn_hide(output_diff):
    if output_diff:
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)


TITLE = """
    <div style="display: inline-flex;">
        <div style="margin-left: 6px; font-size:32px; color: #6366f1"><b>NCHC</b> 學術翻譯服務</div>
    </div>
"""

CSS = """
    h1 {
        text-align: center;
        display: block;
        height: 10vh;
        align-content: center;
    }
    footer {
        visibility: hidden;
    }
    .menu_btn {
        width: 48px;
        height: 48px;
        max-width: 48px;
        min-width: 48px;
        padding: 0px;
        background-color: transparent;
        border: none;
        cursor: pointer;
        position: relative;
        box-shadow: none;
    }
    .menu_btn::before,
    .menu_btn::after {
        content: '';
        position: absolute;
        width: 30px;
        height: 3px;
        background-color: #4f46e5;
        transition: transform 0.3s ease;
    }
    .menu_btn::before {
        top: 12px;
        box-shadow: 0 8px 0 #6366f1;
    }
    .menu_btn::after {
        bottom: 16px;
    }
    .menu_btn.active::before {
        transform: translateY(8px) rotate(45deg);
        box-shadow: none;
    }
    .menu_btn.active::after {
        transform: translateY(-8px) rotate(-45deg);
    }
    .lang {
        max-width: 100px;
        min-width: 100px;
    }
"""

JS = """
    function () {
        const menu_btn = document.getElementById('menu');
        menu_btn.classList.toggle('active');
    }

"""

with gr.Blocks(theme="soft", css=CSS, fill_height=True) as demo:
    with gr.Row():
        visible = gr.State(value=True)
        menu_btn = gr.Button(
            value="", elem_classes="menu_btn", elem_id="menu", size="sm"
        )
        gr.HTML(TITLE)
    with gr.Row():
        with gr.Column(scale=1) as menubar:
            endpoint = gr.Dropdown(
                label="Endpoint",
                choices=["OpenAI", "Groq", "TogetherAI", "Ollama", "CUSTOM"],
                value="CUSTOM",
                visible=False,                
            )
            choice = gr.Checkbox(
                label="Additional Endpoint",
                info="Additional endpoint for reflection",
                visible=False,
            )
            model = gr.Dropdown(
                label="執行翻譯模型 (1,3輪)",
                #value="taide-llama2-70b",
                choices=["taide-llama2-70b"],
                value="taide-llama2-70b",
            )
            api_key = gr.Textbox(
                label="API_KEY",
                type="password",
                visible=False,                
            )
            base = gr.Textbox(label="BASE URL", visible=False)
            endpoint2 = gr.Dropdown(
                label="Additional Endpoint",
                choices=[
                    "OpenAI",
                    "Groq",
                    "TogetherAI",
                    "Ollama",
                    "CUSTOM2",
                ],
                value="CUSTOM2",
                visible=False,                
            )
            model2 = gr.Dropdown(
                label="評論翻譯模型 (第2輪)",
                choices=["01-ai/yi-large","nvidia/nemotron-4-340b-instruct", "meta/llama-3.1-70b-instruct"],
                value="meta/llama-3.1-70b-instruct",
            )
            api_key2 = gr.Textbox(
                label="API_KEY",
                type="password",
                visible=False,                
            )
            base2 = gr.Textbox(label="BASE URL", visible=False)
            with gr.Row():
                source_lang = gr.Textbox(
                    label="輸入 Lang",
                    value="English",
                    elem_classes="lang",
                )
                target_lang = gr.Textbox(
                    label="翻譯 Lang",
                    value="台灣用的中文",
                    elem_classes="lang",
                )
            switch_btn = gr.Button(value="🔄️")
            country = gr.Textbox(
                label="國家區域", value="台灣", max_lines=1
            )
            with gr.Accordion("進階設定", open=False):
                max_tokens = gr.Slider(
                    label="Max tokens Per Chunk",
                    minimum=512,
                    maximum=2046,
                    value=1000,
                    step=8,
                )
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0,
                    maximum=1.0,
                    value=0.3,
                    step=0.1,
                )
                rpm = gr.Slider(
                    label="Request Per Minute",
                    minimum=1,
                    maximum=1000,
                    value=60,
                    step=1,
                )

        with gr.Column(scale=4):
            source_text = gr.Textbox(
                label="輸入文字",
                value="One of the major barriers to using large language models (LLMs) in medicine is the perception they use uninterpretable methods to make clinical decisions that are inherently different from the cognitive processes of clinicians. In this manuscript we develop diagnostic reasoning prompts to study whether LLMs can imitate clinical reasoning while accurately forming a diagnosis. We find that GPT-4 can be prompted to mimic the common clinical reasoning processes of clinicians without sacrificing diagnostic accuracy. This is significant because an LLM that can imitate clinical reasoning to provide an interpretable rationale offers physicians a means to evaluate whether an LLMs response is likely correct and can be trusted for patient care. Prompting methods that use diagnostic reasoning have the potential to mitigate the “black box” limitations of LLMs, bringing them one step closer to safe and effective use in medicine.",
                lines=8,
            )
            with gr.Tab("最終翻譯 (第3輪)"):
                output_final = gr.Textbox(
                    label="最終翻譯", lines=8, show_copy_button=True
                )
            with gr.Tab("初始翻譯 (第1輪)"):
                output_init = gr.Textbox(
                    label="初始翻譯", lines=8, show_copy_button=True
                )
            with gr.Tab("評論翻譯 (第2輪)"):
                output_reflect = gr.Textbox(
                    label="評論翻譯", lines=8, show_copy_button=True
                )
            with gr.Tab("前後修正差異"):
                output_diff = gr.HighlightedText(visible=False)
    with gr.Row():
        submit = gr.Button(value="翻譯")
        upload = gr.UploadButton(label="上傳文件 (TXT, PDF, DOCX)", file_types=["text"])
        export = gr.DownloadButton(visible=False)
        clear = gr.ClearButton(
            [source_text, output_init, output_reflect, output_final]
        )
        close = gr.Button(value="Stop", visible=False)

    switch_btn.click(
        fn=switch,
        inputs=[source_lang, source_text, target_lang, output_final],
        outputs=[source_lang, source_text, target_lang, output_final],
    )

    menu_btn.click(
        fn=update_menu, inputs=visible, outputs=[visible, menubar], js=JS
    )
    endpoint.change(fn=update_model, inputs=[endpoint], outputs=[model, base])

    #choice.select(fn=enable_sec, inputs=[choice], outputs=[AddEndpoint])
    endpoint2.change(
        fn=update_model, inputs=[endpoint2], outputs=[model2, base2]
    )

    start_ta = submit.click(
        fn=huanik,
        inputs=[
            endpoint,
            base,
            model,
            api_key,
            choice,
            endpoint2,
            base2,
            model2,
            api_key2,
            source_lang,
            target_lang,
            source_text,
            country,
            max_tokens,
            temperature,
            rpm,
        ],
        outputs=[output_init, output_reflect, output_final, output_diff],
    )
    upload.upload(fn=read_doc, inputs=upload, outputs=source_text)
    output_diff.change(fn=export_txt, inputs=output_final, outputs=[export])

    submit.click(fn=close_btn_show, outputs=[clear, close])
    output_diff.change(
        fn=close_btn_hide, inputs=output_diff, outputs=[clear, close]
    )
    close.click(fn=None, cancels=start_ta)

if __name__ == "__main__":
    demo.queue(api_open=False).launch(show_api=False, share=True)
