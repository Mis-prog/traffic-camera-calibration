import matplotlib.pyplot as plt
import numpy as np

def plot_residuals_comparison(RESUALDS):
    """
    Строит график сравнения остатков на первом и последнем шаге оптимизации.
    RESUALDS — словарь вида: {step_num: {'metric_name': [values], ...}, ...}
    """
    fig, ax = plt.subplots(figsize=(14, 5))

    step_start = 1
    step_end = max(RESUALDS)

    x_offset = 0
    xticks = []
    xticklabels = []

    keys = list(RESUALDS[step_start].keys())

    def short_name(name):
        """
        Сокращает длинные метки автоматически:
        - оставляет первые буквы слов
        - убирает повторяющиеся шаблоны
        """
        name = name.replace("Расстояние", "R")
        name = name.replace("точки", "T")
        name = name.replace("в", "V")
        name = name.replace("до", "D")
        name = name.replace("линии", "L")
        return ''.join(word[0].upper() for word in name.split() if word)

    for i, key in enumerate(keys):
        y_start = RESUALDS[step_start][key]
        y_end = RESUALDS[step_end][key]
        n = len(y_start)
        x_range = np.arange(n) + x_offset

        # Построение
        ax.plot(x_range, y_start, 'o-', label=f'{key} (step 1)')
        ax.plot(x_range, y_end, 's--', label=f'{key} (step last)')

        # Подписи по оси X
        short_key = short_name(key)
        xticks.extend(x_range)
        xticklabels.extend([f'{short_key}{j}' for j in range(n)])

        # Разделитель между метриками
        if i < len(keys) - 1:
            ax.axvline(x_range[-1] + 0.5, color='gray', linestyle='--')

        x_offset += n

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=90, fontsize=8)

    ax.set_ylabel("Residual value")
    ax.set_title("Сравнение остатков на первом и последнем шаге")
    ax.legend(fontsize=8)
    ax.grid(True)
    plt.tight_layout()
    plt.show()
