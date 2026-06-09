import gradio as gr
from query import ask


def handle_query(question):
    if not question.strip():
        return "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="GSU Professor Guide") as demo:
    gr.Markdown("## GSU Unofficial Professor Guide")
    gr.Markdown("Ask questions about Grambling State University professors based on student reviews.")

    inp = gr.Textbox(label="Your question", placeholder="e.g. Is Professor McGowan an easy class to pass?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
