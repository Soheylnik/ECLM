import os
import re

def convert_to_txt(directory_path):
    """
    این تابع تمام فایل‌ها در دایرکتوری و زیرپوشه‌های آن را به فرمت .txt تغییر نام می‌دهد
    و نام اصلی فایل‌ها را در یک دیکشنری ذخیره می‌کند.
    """
    original_extensions = {}  # دیکشنری برای ذخیره نام فایل‌های اصلی
    txt_files = []

    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith('.txt'):
                new_filename = f"{os.path.splitext(filename)[0]}.txt"
                new_file_path = os.path.join(root, new_filename)
                try:
                    if os.path.exists(file_path):
                        os.rename(file_path, new_file_path)
                        print(f'{filename} به {new_filename} تغییر یافت.')
                        txt_files.append(new_file_path)
                        original_extensions[new_file_path] = filename  # ذخیره نام و پسوند اصلی
                    else:
                        print(f'فایل اصلی {file_path} پیدا نشد و نمی‌توان آن را تغییر نام داد.')
                except Exception as e:
                    print(f'خطا در تغییر نام فایل {filename}: {e}')
            else:
                txt_files.append(file_path)

    return txt_files, original_extensions

def revert_to_original_format(original_extensions):
    """
    این تابع فایل‌های تغییر نام داده شده را به پسوند اصلی خود بازمی‌گرداند.
    """
    for txt_file, original_name in original_extensions.items():
        original_path = os.path.join(os.path.dirname(txt_file), original_name)
        try:
            os.rename(txt_file, original_path)
            print(f'{txt_file} به {original_name} بازگردانده شد.')
        except Exception as e:
            print(f'خطا در تغییر نام فایل {txt_file} به {original_name}: {e}')

def is_absolute_url(url):
    """
    این تابع بررسی می‌کند که آیا یک URL مطلق است یا نسبی.
    URL‌های مطلق با پروتکل‌هایی مانند http://، https://، //، data: شروع می‌شوند.
    """
    absolute_url_patterns = (
        'http://',
        'https://',
        '//',
        'data:',
    )
    return url.startswith(absolute_url_patterns)

def modify_href_src_in_files(txt_files, search_sim_text='some_similar_text'):
    """
    این تابع فایل‌های .txt را پردازش می‌کند تا ویژگی href در تگ‌های <link>، 
    ویژگی src در تگ‌های <script> و ویژگی src در تگ‌های <img> را به قالب {% static '...' %} تغییر دهد
    مگر اینکه قبلاً شامل {% static %}، {{ ... }} باشند یا URL مطلق باشد.
    همچنین جستجوی متنی مشابه در خطوط انجام می‌دهد و نتایج را در فایل‌های لاگ ذخیره می‌کند.
    """
    search_results = []
    search_sim_results = []
    found_any = False

    # الگوی regex برای پیدا کردن تگ‌های <link> با ویژگی href
    link_tag_regex = re.compile(r'<link\b[^>]*href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    # الگوی regex برای پیدا کردن تگ‌های <script> با ویژگی src
    script_tag_regex = re.compile(r'<script\b[^>]*src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    # الگوی regex برای پیدا کردن تگ‌های <img> با ویژگی src
    img_tag_regex = re.compile(r'<img\b[^>]*src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        try:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
        except Exception as e:
            print(f'خطا در باز کردن فایل {txt_file}: {e}')
            continue

        modified = False  # علامت برای بررسی تغییرات

        # پردازش هر خط در فایل
        for line_num, line in enumerate(lines, start=1):
            original_line = line  # نگهداری نسخه اصلی خط برای مقایسه

            # پردازش ویژگی href در تگ‌های <link>
            if '<link' in line:
                matches = link_tag_regex.finditer(line)
                for match in matches:
                    original_content = match.group(1)

                    # بررسی وجود قالب‌های Django در محتوای href یا URL مطلق
                    if ('{%' in original_content or '%}' in original_content or 
                        '{{' in original_content or '}}' in original_content or 
                        is_absolute_url(original_content)):
                        search_results.append(f'{filename}:{line_num} ---> href="{original_content}" (has {{%}}، {{}} یا URL مطلق)')
                        continue

                    # تغییر href به قالب {% static '...' %}
                    new_content = f'{{% static \'{original_content}\' %}}'
                    # جایگزینی محتوای جدید در خط
                    new_href_attribute = f'href="{new_content}"'
                    line = re.sub(r'href\s*=\s*["\']([^"\']+)["\']', new_href_attribute, line, count=1)
                    search_results.append(f'{filename}:{line_num} ---> Updated href="{new_content}"')
                    modified = True
                    found_any = True

            # پردازش ویژگی src در تگ‌های <script>
            if '<script' in line:
                matches = script_tag_regex.finditer(line)
                for match in matches:
                    original_content = match.group(1)

                    # بررسی وجود قالب‌های Django در محتوای src یا URL مطلق
                    if ('{%' in original_content or '%}' in original_content or 
                        '{{' in original_content or '}}' in original_content or 
                        is_absolute_url(original_content)):
                        search_results.append(f'{filename}:{line_num} ---> src="{original_content}" (has {{%}}، {{}} یا URL مطلق)')
                        continue

                    # تغییر src به قالب {% static '...' %}
                    new_content = f'{{% static \'{original_content}\' %}}'
                    # جایگزینی محتوای جدید در خط
                    new_src_attribute = f'src="{new_content}"'
                    line = re.sub(r'src\s*=\s*["\']([^"\']+)["\']', new_src_attribute, line, count=1)
                    search_results.append(f'{filename}:{line_num} ---> Updated src="{new_content}"')
                    modified = True
                    found_any = True

            # پردازش ویژگی src در تگ‌های <img>
            if '<img' in line:
                matches = img_tag_regex.finditer(line)
                for match in matches:
                    original_content = match.group(1)

                    # بررسی وجود قالب‌های Django در محتوای src یا URL مطلق
                    if ('{%' in original_content or '%}' in original_content or 
                        '{{' in original_content or '}}' in original_content or 
                        is_absolute_url(original_content)):
                        search_results.append(f'{filename}:{line_num} ---> src="{original_content}" (has {{%}}، {{}} یا URL مطلق)')
                        continue

                    # تغییر src به قالب {% static '...' %}
                    new_content = f'{{% static \'{original_content}\' %}}'
                    # جایگزینی محتوای جدید در خط
                    new_src_attribute = f'src="{new_content}"'
                    line = re.sub(r'src\s*=\s*["\']([^"\']+)["\']', new_src_attribute, line, count=1)
                    search_results.append(f'{filename}:{line_num} ---> Updated src="{new_content}"')
                    modified = True
                    found_any = True

            # جستجوی متن مشابه در خط
            if search_sim_text in line:
                search_sim_results.append(f'{filename}:{line_num} ---> Not Updated{line.strip()}')

            # به‌روزرسانی خط اگر تغییر کرده باشد
            if line != original_line:
                lines[line_num - 1] = line

        # نوشتن تغییرات در فایل اگر تغییراتی اعمال شده باشد
        if modified:
            try:
                with open(txt_file, 'w', encoding='utf-8', errors='ignore') as file:
                    file.writelines(lines)
                print(f'تغییرات در {txt_file} اعمال شد.')
            except Exception as e:
                print(f'خطا در نوشتن به فایل {txt_file}: {e}')

    # نوشتن نتایج تغییرات href و src در search_result.txt
    if search_results:
        with open('search_result.txt', 'w', encoding='utf-8') as search_result:
            for result in search_results:
                search_result.write(f"{result}\n")

    # نوشتن نتایج جستجوی متن مشابه در search_sim.txt
    if search_sim_results:
        with open('search_sim.txt', 'w', encoding='utf-8') as search_sim:
            for sim_result in search_sim_results:
                search_sim.write(f"{sim_result}\n")

    if not found_any and not search_sim_results:
        print('nop, no one is here')

def find_and_modify_files(directory_path):
    """
    این تابع اصلی است که فایل‌ها را به .txt تغییر نام می‌دهد، ویژگی‌های href و src را تغییر می‌دهد،
    متون مشابه را جستجو می‌کند، و پس از آن نام فایل‌ها را به فرمت اصلی بازمی‌گرداند.
    """
    # تبدیل فایل‌ها به .txt و دریافت نام‌های اصلی
    txt_files, original_extensions = convert_to_txt(directory_path)

    # تغییر ویژگی‌های href و src در فایل‌های .txt و جستجوی متون مشابه
    modify_href_src_in_files(txt_files, search_sim_text='some_similar_text')  # می‌توانید 'some_similar_text' را تغییر دهید

    # بازگرداندن فایل‌ها به پسوند اصلی
    revert_to_original_format(original_extensions)

# فراخوانی اصلی برنامه
if __name__ == "__main__":
    # تعریف مسیر دایرکتوری
    directory_path = 'templates'  # به مسیر صحیح خود تغییر دهید

    # بررسی وجود دایرکتوری 
    if not os.path.isdir(directory_path): 
        print(f'دایرکتوری {directory_path} وجود ندارد.') 
    else: 
        find_and_modify_files(directory_path)
