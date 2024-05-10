import re


def tokenize(text):
    """一个按一个中文字符或者英文字符为一个token切割并返回token数量的函数"""
    # 使用正则表达式匹配汉字、英文字母、标点符号，忽略换行符和空格
    pattern = r'[\u4e00-\u9fa5]|[a-zA-Z]|\\p{P}'
    tokens = re.findall(pattern, text)
    return len(tokens)


def merge_and_output(cut_texts, size):
    """一个按size要求返回倒序文本段的函数"""
    if not cut_texts:  # 如果cut_texts为空，则不做任何动作
        return ''

        # 检查最后一个元素的token数
    tokens = tokenize(cut_texts[-1])
    if tokens > size:
        # 如果大于size个tokens，则直接输出最后一个元素
        print(cut_texts[-1])
        return cut_texts[-1]

        # 如果最后一个元素的token数小于size，则开始合并
    merged_text = cut_texts[-1]
    while len(cut_texts) > 1:
        tokens = tokenize(merged_text)
        if tokens > size:
            break  # 如果合并后的字符串token数大于size，则跳出循环

        # 合并前一个元素和当前合并的文本
        prev_text = cut_texts.pop(-2)  # 移除倒数第二个元素并返回它
        merged_text = prev_text + ' ' + merged_text

        # 输出最终合并的字符串
    print(merged_text)
    return merged_text

def cut_text_by_rules(text, size=29):
    """一个按\n和。进行分割，并按size要求返回倒序文本段的函数"""
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

    end_cut_texts = merge_and_output(cut_texts, size=size)

    print("最终cut_texts：", end_cut_texts)

    return end_cut_texts


# 示例文本
text = """  
运行这段代码后，docs列表中第二个Document对象的text属性值将会从"6789"变为"3456789"，因为"12345"的后三个字符是"345"，所以拼接后的结果就是"3456789"。  

请注意，这段代码假设docs列表中至少有两个元素，并且每个元素的text属性值长度都足够进行重叠操作（即长度至少为overlap_length）。如果列表中元素不足或者text值长度不够，代码可能会引发错误。在实际应用中，你可能需要添加一些错误检查机制来处理这些异常情况。  
"""

# 对文本进行切割
cut_texts = cut_text_by_rules(text)

print(f"Cut Text:\n{cut_texts}\n")