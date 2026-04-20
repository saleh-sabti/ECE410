// gemm_tiled.cu — shared-memory tiled 1024x1024 FP32 GEMM, tile size T=8
#include <stdio.h>
#include <cuda_runtime.h>

#define N 1024
#define T 8

__global__ void gemm_tiled(float *A, float *B, float *C, int n) {
    __shared__ float As[T][T];
    __shared__ float Bs[T][T];

    int row = blockIdx.y * T + threadIdx.y;
    int col = blockIdx.x * T + threadIdx.x;
    float acc = 0.0f;

    for (int t = 0; t < n / T; t++) {
        As[threadIdx.y][threadIdx.x] = A[row * n + t * T + threadIdx.x];
        Bs[threadIdx.y][threadIdx.x] = B[(t * T + threadIdx.y) * n + col];
        __syncthreads();

        for (int k = 0; k < T; k++)
            acc += As[threadIdx.y][k] * Bs[k][threadIdx.x];
        __syncthreads();
    }

    if (row < n && col < n)
        C[row * n + col] = acc;
}

int main() {
    size_t bytes = (size_t)N * N * sizeof(float);
    float *h_A = (float*)malloc(bytes);
    float *h_B = (float*)malloc(bytes);
    float *h_C = (float*)malloc(bytes);

    for (int i = 0; i < N * N; i++) { h_A[i] = 1.0f; h_B[i] = 1.0f; }

    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);
    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);

    dim3 block(T, T);
    dim3 grid(N / T, N / T);

    // warmup
    gemm_tiled<<<grid, block>>>(d_A, d_B, d_C, N);
    cudaDeviceSynchronize();

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    gemm_tiled<<<grid, block>>>(d_A, d_B, d_C, N);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms = 0;
    cudaEventElapsedTime(&ms, start, stop);

    double flops = 2.0 * N * N * N;
    double gflops = flops / (ms / 1000.0) / 1e9;
    printf("gemm_tiled: %.2f ms, %.2f GFLOP/s\n", ms, gflops);

    cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost);
    printf("C[0][0] = %.1f (expected %d)\n", h_C[0], N);

    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    free(h_A); free(h_B); free(h_C);
    cudaEventDestroy(start); cudaEventDestroy(stop);
    return 0;
}
