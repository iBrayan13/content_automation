from typing import List, Tuple, Any, Literal, Optional

from faster_whisper import WhisperModel

class SubtitleGenerator:

    def __init__(self):
        self.model = WhisperModel("medium", compute_type="float32")

    def combine_word_segments(self, words: List[Any], max_words: int = 15, min_pause: int = 0.5) -> Optional[List[Tuple[float, float, str]]]:
            try:
                srt_entries = []
                chunk = []

                for word in words:
                    if not chunk:
                        chunk.append(word)
                        continue

                    pause = word.start - chunk[-1].end
                    if len(chunk) >= max_words or pause > min_pause or chunk[-1].word.strip()[-1:] in ".!?,":
                        start = chunk[0].start
                        end = chunk[-1].end
                        text = ' '.join([w.word for w in chunk]).strip()
                        srt_entries.append((start, end, text))
                        chunk = [word]
                    else:
                        chunk.append(word)

                if chunk:
                    start = chunk[0].start
                    end = chunk[-1].end
                    text = ' '.join([w.word for w in chunk]).strip()
                    srt_entries.append((start, end, text))

                return srt_entries
            
            except Exception as e:
                print(f"Error in combine_word_segments: {e}")
                return None

    def word_by_word_segments(self, words: List[Any]) -> Optional[List[Tuple[float, float, str]]]:
        try:
            srt_entries = []
            for word in words:
                start = word.start
                end = word.end
                text = word.word.strip()
                if text:
                    srt_entries.append((start, end, text))
            return srt_entries
        
        except Exception as e:
            print(f"Error in word_by_word_segments: {e}")
            return None

    def format_timestamp(self, seconds: int |  float) -> str:
        ms = int((seconds - int(seconds)) * 1000)
        s = int(seconds)
        h = s // 3600
        m = (s % 3600) // 60
        s = s % 60
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    # 🧠 Transcribe and translate function
    def get_subtitles(self, audio_file: str, str_name: str, segment_type: Literal['word', 'sentence']) -> Optional[str]:
        try:
            segments, info = self.model.transcribe(audio_file, beam_size=5, word_timestamps=True)

            # Create SRT
            all_words = []
            for segment in segments:
                if segment.words:
                    all_words.extend(segment.words)

            if segment_type == 'word':
                srt_chunks = self.word_by_word_segments(all_words)
            elif segment_type == 'sentence':
                srt_chunks = self.combine_word_segments(all_words)
            else:
                raise ValueError("Invalid segment_type. Choose 'word' or 'sentence'.")
            
            if srt_chunks is None:
                raise ValueError("No segments found.")

            original_srt_path = f"temp/{str_name}.srt"
            with open(original_srt_path, "w", encoding="utf-8") as f:
                for idx, (start, end, text) in enumerate(srt_chunks, start=1):
                    f.write(f"{idx}\n{self.format_timestamp(start)} --> {self.format_timestamp(end)}\n{text}\n\n")

            return original_srt_path
        
        except Exception as e:
            print(f"Error in get_subtitles: {e}")
            return None