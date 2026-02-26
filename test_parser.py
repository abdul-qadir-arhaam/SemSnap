from parser import get_text_from_file, extract_subjects_and_marks

file_path = input("Enter file path: ")

text = get_text_from_file(file_path)

print("\n===== RAW EXTRACTED TEXT =====\n")
print(text[:1000])   # print first 1000 characters

subjects = extract_subjects_and_marks(text)

print("\n===== DETECTED SUBJECTS =====\n")
print(subjects)