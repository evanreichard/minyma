from io import TextIOWrapper
import json

class DataNormalizer():
    def __init__(self, file: TextIOWrapper):
        self.file = file

    def __len__(self) -> int:
        return 0

    def __iter__(self):
        yield None


class PubMedNormalizer(DataNormalizer):
    """
    Iterator class that takes a file and iterates over each line. Data is
    normalized inside the iterator.
    """
    def __init__(self, file: TextIOWrapper):
        self.name = "pubmed"
        self.file = file
        self.length = 0

    def __len__(self):
        last_pos = self.file.tell()
        self.length = sum(1 for _ in self.file)
        self.file.seek(last_pos)
        return self.length

    def __iter__(self):
        count = 0

        # Iterate over each line in self.file, normalize, increment counter,
        # and yield the normalized data.
        while True:
            line = self.file.readline()

            # EOF
            if not line:
                break

            # Load JSON
            l = json.loads(line, strict=False)
            norm_text = l.get("text").lower()

            # Using the second occurance of "text mining" as a break point. We
            # only capture what follows. Initially tried using regular
            # expressions, but this is significantly faster.
            split_data = norm_text.split("text mining")
            norm_text = "text mining".join(split_data[2:])
            norm_text = "\n".join(norm_text.split("\n")[1:])

            count += 1

            # ID = Line Number
            yield {
               "id": str(count - 1),
               "doc": norm_text,
               "metadata": {
                   "file": l.get("file")
               },
           }
