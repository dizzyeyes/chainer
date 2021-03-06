import numpy
from chainer import cuda, Function

def _kern():
    return cuda.elementwise(
        'float* y, const float* cond, const float* x, float slope',
        'y[i] = cond[i] >= 0 ? x[i] : slope * x[i]', 'lrelu')

class LeakyReLU(Function):
    """Leaky rectifier unit."""

    def __init__(self, slope=0.2):
        self.slope = slope

    def forward_cpu(self, x):
        y = x[0].copy()
        y[x[0] < 0] *= self.slope
        return y,

    def forward_gpu(self, x):
        y = cuda.empty_like(x[0])
        _kern()(y, x[0], x[0], self.slope)
        return y,

    def backward_cpu(self, x, gy):
        gx = gy[0].copy()
        gx[x[0] < 0] *= self.slope
        return gx,

    def backward_gpu(self, x, gy):
        gx = cuda.empty_like(x[0])
        _kern()(gx, x[0], gy[0], self.slope)
        return gx,

def leaky_relu(x, slope=0.2):
    """Leaky Rectified Linear Unit function.

    This function is expressed as :math:`f(x) = \max(x, ax)`, where :math:`a` is
    a configurable slope value.

    Args:
        x (~chainer.Variable): Input variable.
        slope (float): Slope value :math:`a`.

    Returns:
        ~chainer.Variable: Output variable.

    """
    return LeakyReLU(slope)(x)
