import AudioTranscribe
from KwsUi import KwsUi


def main():
    KwsUi()
    # input_file_path = "recordings/english1.mp3"
    #
    # tr = transcribe(input_file_path)
    # print("Prediction: {}".format(tr.hyp().hypstr))
    # print("Accuracy: {}".format(calculate_accuracy(tr.hyp().hypstr)))
    #
    # kwr = keyword_search(input_file_path, [
    #     ("peas", 20),
    #     ("store", 20),
    #     ("thick", 10),
    # ])
    #
    # print_segments(reversed(list(kwr.seg())))
    # at = AudioTranscribe_ds
    # print(at.transcribe("data/test/test_cut.wav", None))


if __name__ == "__main__":
    main()
