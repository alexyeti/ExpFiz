import matplotlib.pyplot as plt

def plot_trajectory(trajectory):
    """Генерация графика траектории"""
    x, y = trajectory[:, 0], trajectory[:, 1]
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', label='Траектория')
    plt.scatter(x[-1], y[-1], color='red', label='Точка падения')
    plt.title("Траектория полета объекта")
    plt.xlabel("Расстояние (м)")
    plt.ylabel("Высота (м)")
    plt.legend()
    plt.grid()
    plt.savefig("trajectory.png", dpi=400)
    plt.close()