def tokenize_chinese_text(text):
    # 使用正则表达式简单地将连续的中文字符、英文字母、数字视为一个token
    # 这里为了简化，我们不考虑其他标点符号，只将中文字符、英文字母和数字视为token
    tokens = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or 'a' <= char <= 'z' or 'A' <= char <= 'Z' or '0' <= char <= '9':
            tokens.append(char)
            # 可以根据需要添加更多字符分类
    return tokens


def cut_text_by_rules(text, size=120):
    cut_texts = []  # 存储最终切割好的文本段

    # 第一步：先以“\n”为分隔符进行切割
    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        paragraph = paragraph.strip()  # 去除首尾的空白字符
        if not paragraph:
            continue  # 跳过空段落

        # 第二步：再按“。”进行切割
        sentences = paragraph.split('。')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:  # 跳过空句子
                cut_texts.append(sentence + '。')  # 添加句子，并补回句号

    print("初步分割cut_texts：", cut_texts)

    while len(cut_texts) > 0:
        last_text = cut_texts[-1]
        # 假设我们使用非空白字符作为token的简单分词方法
        tokens = last_text.split()
        if len(tokens) > size:
            print(last_text)  # 输出token数量大于200的文本
            break  # 既然已经找到一个大于200的，就停止合并
        else:
            # 如果小于200，则合并倒数第一和倒数第二个文本
            if len(cut_texts) == 1:
                print("All texts have been merged and none exceeded 200 tokens.")
                break
            else:
                cut_texts[-2] = cut_texts[-2] + ' ' + last_text
                cut_texts.pop()  # 移除已合并的最后一个文本

    print("最终cut_texts：", cut_texts)

    return cut_texts


# 示例文本
text = """  
运行这段代码后，docs列表中第二个Document对象的text属性值将会从"6789"变为"3456789"，因为"12345"的后三个字符是"345"，所以拼接后的结果就是"3456789"。  

请注意，这段代码假设docs列表中至少有两个元素，并且每个元素的text属性值长度都足够进行重叠操作（即长度至少为overlap_length）。如果列表中元素不足或者text值长度不够，代码可能会引发错误。在实际应用中，你可能需要添加一些错误检查机制来处理这些异常情况。  
"""

# 对文本进行切割
cut_texts = cut_text_by_rules(text)
for i, cut_text in enumerate(cut_texts):
    print(f"Cut Text {i + 1}:\n{cut_text}\n")