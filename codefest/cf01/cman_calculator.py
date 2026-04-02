#!/usr/bin/env python3
"""
CMAN Calculator - Roofline Analysis for Neural Networks
Computes: MACs, Parameters, Memory, Arithmetic Intensity

Author: Saleh Sabti
Course: ECE 410/510
"""

def calculate_cman(layers):
    """
    Calculate CMAN metrics for a neural network.

    Args:
        layers: List of tuples (input_dim, output_dim) for each fully-connected layer

    Returns:
        Dictionary with calculated metrics
    """

    results = {
        'layers_metrics': [],
        'total_macs': 0,
        'total_params': 0,
        'weight_memory_bytes': 0,
        'activation_memory_bytes': 0,
        'arithmetic_intensity': 0.0
    }

    bytes_per_param = 4  # FP32

    # Calculate per-layer metrics
    for i, (input_dim, output_dim) in enumerate(layers, 1):
        macs = input_dim * output_dim
        params = input_dim * output_dim  # Fully-connected layer
        weight_bytes = params * bytes_per_param

        results['layers_metrics'].append({
            'layer': i,
            'input_dim': input_dim,
            'output_dim': output_dim,
            'macs': macs,
            'params': params,
            'weight_bytes': weight_bytes
        })

        results['total_macs'] += macs
        results['total_params'] += params
        results['weight_memory_bytes'] += weight_bytes

    # Calculate activation memory (input + all layer outputs)
    for i, (input_dim, output_dim) in enumerate(layers):
        results['activation_memory_bytes'] += output_dim * bytes_per_param

    # Add initial input dimension to activation memory
    if layers:
        results['activation_memory_bytes'] += layers[0][0] * bytes_per_param

    # Calculate arithmetic intensity
    total_memory = results['weight_memory_bytes'] + results['activation_memory_bytes']
    total_flops = 2 * results['total_macs']  # MACs = 1 FLOP, but multiply-add = 2 FLOPs

    if total_memory > 0:
        results['arithmetic_intensity'] = total_flops / total_memory

    return results


def print_cman_report(results):
    """Pretty print CMAN analysis report."""

    print("\n" + "="*70)
    print("CMAN CALCULATOR - Roofline Analysis Report")
    print("="*70)

    # Per-layer metrics
    print("\na. MACs per layer")
    print("-" * 70)
    for m in results['layers_metrics']:
        print(f"  * Layer {m['layer']}: {m['input_dim']} × {m['output_dim']} = {m['macs']:,} MACs")

    # Total MACs
    print("\nb. Total MACs")
    print("-" * 70)
    print(f"  * Sum of all layers = {results['total_macs']:,} MACs")

    # Total parameters
    print("\nc. Total trainable parameters")
    print("-" * 70)
    print(f"  * Same as total MACs ⟹ {results['total_params']:,} parameters")

    # Weight memory
    print("\nd. Weight memory (FP32)")
    print("-" * 70)
    weight_kb = results['weight_memory_bytes'] / 1024
    print(f"  * {results['total_params']:,} × 4 bytes = {results['weight_memory_bytes']:,} bytes ⟹ {weight_kb:.1f} KB")

    # Activation memory
    print("\ne. Activation memory")
    print("-" * 70)
    print(f"  * Store input + all layer outputs")
    print(f"  * = (input + layer outputs) × 4 bytes = {results['activation_memory_bytes']:,} bytes ⟹ {results['activation_memory_bytes']/1024:.1f} KB")

    # Arithmetic intensity
    print("\nf. Arithmetic intensity")
    print("-" * 70)
    total_memory = results['weight_memory_bytes'] + results['activation_memory_bytes']
    total_flops = 2 * results['total_macs']
    print(f"  * AI = (2 × total MACs) / (weight bytes + activation bytes)")
    print(f"  * = (2 × {results['total_macs']:,}) / ({results['weight_memory_bytes']:,} + {results['activation_memory_bytes']:,})")
    print(f"  * = {total_flops:,} / {total_memory:,}")
    print(f"  * ≈ {results['arithmetic_intensity']:.3f} FLOP/byte")

    # Interpretation
    print("\nINTERPRETATION:")
    print("-" * 70)
    if results['arithmetic_intensity'] < 0.1:
        print(f"  • MEMORY-BOUND: AI={results['arithmetic_intensity']:.3f} is very low")
        print(f"    Network is starved for compute; memory is the bottleneck")
    elif results['arithmetic_intensity'] < 1.0:
        print(f"  • MEMORY-BOUND: AI={results['arithmetic_intensity']:.3f} is low (<1)")
        print(f"    Memory bandwidth is still a constraint")
    else:
        print(f"  • COMPUTE-BOUND: AI={results['arithmetic_intensity']:.3f} is high")
        print(f"    Arithmetic throughput is the bottleneck, not memory")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Example: CMAN assignment (MNIST-like network)
    # Layers: 784 -> 256 -> 128 -> 10
    layers = [
        (784, 256),
        (256, 128),
        (128, 10)
    ]

    results = calculate_cman(layers)
    print_cman_report(results)

    # You can also programmatically access results:
    print(f"Computed metrics:")
    print(f"  Total MACs: {results['total_macs']:,}")
    print(f"  Arithmetic Intensity: {results['arithmetic_intensity']:.3f} FLOP/byte")
