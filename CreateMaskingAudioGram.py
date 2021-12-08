import csv

import numpy as np
import simpleaudio as sa

# Hyper params
FIRST_SOUND_FREQUENCY           = 400   # [Hz]
FIRST_SOUND_SENSORYLEVEL        = 50    # [dB]
QUANTIZATION_BIT_RATE           = 16    # [bit]
SAMPLING_RATE                   = 44100 # [Hz]
MIN_AMPLITUDE                   = 0.0001
AMPLITUDE_INTERVAL              = 0.0001
CHECK_SECOND_SOUND_FREQUENCYS   = (500, 600, 700, 800, 900, 1000) # List of checking second sound frequencys[Hz] for creating masking audiogram
SENSORYLEVEL_INTERVAL           = 1     # [dB]

assert QUANTIZATION_BIT_RATE % 8 == 0

def Amplitude2SensoryLevel(amplitude, base):
    return 20 * np.log10( amplitude / base )

def SensoryLevel2Amplitude(sensory_level, base):
    return np.power(10, sensory_level / 20) * base

def CreateSinSound(freq, amplitude, time_length=1):
    t = np.linspace(0, time_length, int(time_length * SAMPLING_RATE), False)
    sin = np.sin( freq * t * 2 * np.pi )
    sin *= (np.power(2,QUANTIZATION_BIT_RATE) - 1) / np.max(np.abs(sin))

    return amplitude * sin

def StartAudio(sound1, sound2):
    # sound mix
    audio = sound1+sound2

    audio = audio.astype(np.int16)

    #play
    play_obj = sa.play_buffer(audio, 1, int(QUANTIZATION_BIT_RATE / 8), SAMPLING_RATE)
    play_obj.wait_done()

def CheckBaseAmplitude(freq):
    def_audio=CreateSinSound(freq,1)
    def_audio *= (np.power(2,QUANTIZATION_BIT_RATE) - 1) / np.max(np.abs(def_audio))

    print("Check Your minimam audible limit of",freq,"[Hz] Sin Curve")
    print("If hear the sound, Press A Botton, If not hear it,press B")
    input("If you are ready to start, press ENTER...")

    counter=0.

    while True:
        amp = (counter * AMPLITUDE_INTERVAL) + MIN_AMPLITUDE

        print("Amplitude =",amp)

        audio = amp * def_audio

        audio = audio.astype(np.int16)

        play_obj = sa.play_buffer(audio, 1, 2, SAMPLING_RATE)
        play_obj.wait_done()

        s = input("Audible: Press A, Not Audibule: Press Any > ")

        if "A" == s or "a" == s:
            break

        counter += 1.0

    return amp

if __name__ == "__main__":
    with open("output.csv","w",newline="") as fp:
        writer = csv.writer(fp)

        writer.writerows([
            ["Common Settings"],
            ["","quantization bit rate[bit]",QUANTIZATION_BIT_RATE],
            ["","sampling rate[Hz]",SAMPLING_RATE]
        ])

        writer.writerows([
            ["First Sound Settings"],
            ["","Frequency[Hz]",FIRST_SOUND_FREQUENCY],
            ["","Sensory Level[dB]",FIRST_SOUND_SENSORYLEVEL]
        ])

        writer.writerows([
            ["Second Sound Settings"],
            ["","Frequency[Hz]","Sensory Level[dB]"]
        ])



        first_sound_base_amplitude = CheckBaseAmplitude(FIRST_SOUND_FREQUENCY)
        print("Your minimam audible limit (Amplitude) of",FIRST_SOUND_FREQUENCY,"[Hz] Sin Curve is", first_sound_base_amplitude)

        first_sound_amplitude = SensoryLevel2Amplitude(FIRST_SOUND_SENSORYLEVEL, first_sound_base_amplitude)
        first_sound = CreateSinSound(FIRST_SOUND_FREQUENCY,first_sound_amplitude)

        print("Check your MaskingAudioGram")

        for frequency in CHECK_SECOND_SOUND_FREQUENCYS:
            print("Second Sound Frequency =",frequency,"[Hz]")
            print("First Check your minimam audible limit")
            second_sound_base_amplitude = CheckBaseAmplitude(frequency)

            counter=0.

            print("Check Start")
            while True:
                #Create second sound
                sens = (counter * SENSORYLEVEL_INTERVAL) + 1.
                second_sound_amplitude = SensoryLevel2Amplitude(sens, second_sound_base_amplitude)
                second_sound = CreateSinSound(frequency,second_sound_amplitude)

                print("Sensory Level:", sens)

                StartAudio(first_sound,second_sound)

                s = input("Audible: Press A, Not Audibule: Press Any > ")

                if "A" == s or "a" == s:
                    break

                counter += 1.0

            writer.writerow(["",frequency,sens])