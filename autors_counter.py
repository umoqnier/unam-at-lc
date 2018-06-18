def perfect_match_counter():
    count = 0
    with open("authors.txt", "r") as f:
        doc = f.read()
        data = doc.split('\n')
        for i, author_row in enumerate(data):
            if i == 0:  # For first element
                continue
            author_data = author_row.split('|')
            prev_row = data[i-1].split('|')
            next_row = data[i+1].split('|')
            current_index = int(author_data[0])
            prev_index = int(prev_row[0])
            try:
                next_index = int(next_row[0])
            except ValueError:  # Last row
                break
            if (current_index == prev_index) or (current_index == next_index):
                print("Skip duplicate index of", author_data[1])
            else:
                if author_data[2] == '1':
                    print("Unique PM found", author_data)
                    count += 1
    print("Total unique PM -->", count)


perfect_match_counter()