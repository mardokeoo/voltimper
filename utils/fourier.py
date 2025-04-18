import numpy as np
from scipy.fft import fft, fftfreq

def analizar_fourier(senal, tiempo, frecuencia_fundamental=None):
    N = len(tiempo)
    T = tiempo[1] - tiempo[0]
    
    yf = fft(senal)
    xf = fftfreq(N, T)[:N//2]
    
    amplitudes = 2/N * np.abs(yf[0:N//2])
    
    if frecuencia_fundamental is None:
        idx_fundamental = np.argmax(amplitudes[1:]) + 1
        frecuencia_fundamental = xf[idx_fundamental]
    
    idx_fund = np.argmin(np.abs(xf - frecuencia_fundamental))
    armonicos = [i for i in range(len(xf)) if i != idx_fund]
    
    potencia_fundamental = amplitudes[idx_fund]**2
    potencia_armonicos = sum(amplitudes[i]**2 for i in armonicos)
    
    thd = np.sqrt(potencia_armonicos) / np.sqrt(potencia_fundamental) if potencia_fundamental > 0 else 0
    
    return {
        'frecuencias': xf,
        'amplitudes': amplitudes,
        'frecuencia_fundamental': frecuencia_fundamental,
        'thd': thd,
        'armonicos': [(xf[i], amplitudes[i]) for i in armonicos if amplitudes[i] > max(amplitudes)*0.01]
    }