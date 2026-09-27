"""Compare API prefill scores against the installed generation reference path."""
import json
import mlx.core as mx
from mlx_vlm.generate import generate_step
from openjevtest.api import Engine, DecisionRequest, ROOT
from PIL import Image, ImageDraw


engine = Engine()
results = []
for name in ('text', 'red_square', 'blue_square'):
    image = None
    if name != 'text':
        image = Image.new('RGB', (256, 256), 'white')
        ImageDraw.Draw(image).rectangle((32, 32, 223, 223), fill='red' if name == 'red_square' else 'blue')
    req = DecisionRequest(query='My account was charged twice.' if image is None else 'Evaluate the image.',
                          criterion='Was the account charged twice?' if image is None else 'Is the central square red?')
    inputs = engine.inputs(req, image)
    direct = engine.forward(inputs)
    captured = {}

    def capture(tokens, logits):
        if 'logits' not in captured:
            captured['logits'] = logits
        return logits

    kwargs = {k: v for k, v in inputs.items() if k not in ('input_ids', 'pixel_values', 'attention_mask')}
    step = generate_step(inputs['input_ids'], engine.model, inputs.get('pixel_values'),
                         inputs.get('attention_mask'), max_tokens=1, temperature=0,
                         logits_processors=[capture], **kwargs)
    next(step)
    raw = captured['logits']
    mx.eval(raw)
    mx.synchronize()
    reference = [float(raw[0, i].item()) for i in engine.ids]
    del step
    delta = max(abs(a-b) for a, b in zip(direct, reference))
    # BF16 kernels may differ by a small rounding amount across execution paths.
    assert delta <= 0.125, (name, direct, reference)
    assert (direct[0] > direct[1]) == (reference[0] > reference[1])
    results.append({'case': name, 'direct': direct, 'reference': reference, 'max_abs_delta': delta})
    mx.clear_cache()
target = ROOT / 'results/forward_equivalence.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps({'passed': True, 'tolerance': 0.125, 'cases': results}, indent=2) + '\n')
print(target.read_text())
