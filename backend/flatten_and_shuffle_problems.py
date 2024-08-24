import os
import random

# 기본 디렉토리 설정
base_dir = "/Users/yuseunghun/Documents/onlinejudge_basic"

# 새 폴더 이름 카운터 초기화
new_folder_counter = 1

# 모든 problem-export 폴더 찾기
for folder in os.listdir(base_dir):
    if folder.startswith("problem-export"):
        problem_export_path = os.path.join(base_dir, folder)

        # problem-export 폴더 안의 모든 숫자 이름 폴더 찾기
        numeric_subfolders = [subfolder for subfolder in os.listdir(problem_export_path) if subfolder.isdigit()]
        for subfolder in sorted(numeric_subfolders, key=int):
            old_path = os.path.join(problem_export_path, subfolder)
            new_path = os.path.join(base_dir, str(new_folder_counter))

            # 폴더 이름 바꾸기
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} to {new_path}")

            # 카운터 증가
            new_folder_counter += 1

print(f"Renamed {new_folder_counter - 1} folders.")

# 1부터 new_folder_counter-1까지의 숫자 리스트 생성
folder_numbers = list(range(1, new_folder_counter))

# 숫자 리스트를 랜덤하게 섞기
random.shuffle(folder_numbers)

# 폴더 이름을 랜덤하게 바꾸기
for i, new_number in enumerate(folder_numbers, 1):
    old_path = os.path.join(base_dir, str(i))
    new_path = os.path.join(base_dir, str(new_number))

    # 임시 이름으로 먼저 바꾸기 (중복 방지)
    temp_path = os.path.join(base_dir, f"temp_{i}")
    os.rename(old_path, temp_path)

# 임시 이름을 최종 이름으로 바꾸기
for i in range(1, new_folder_counter):
    temp_path = os.path.join(base_dir, f"temp_{i}")
    new_path = os.path.join(base_dir, str(folder_numbers[i - 1]))
    os.rename(temp_path, new_path)
    print(f"Randomly renamed folder {i} to {folder_numbers[i - 1]}")

print("All folders have been randomly renamed.")