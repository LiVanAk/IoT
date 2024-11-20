## 串口通讯

串口通讯线由管脚 PD_SCK 和 DOUT 组成，用来输出数据，选择输入通道和增益。当数据输出管脚 DOUT 为高电平时，表明A/D 转换器还未准备好输出数据，此时串口时钟输入信号 PD_SCK 应为低电平。当 DOUT 从高电平变低电平后，PD_SCK 应输入 25 至 27 个不等的时钟脉冲（图二）。其中第一个时钟脉冲的上升沿 将读出输出 24 位数据的最高位（MSB），直至第 24 个时钟脉冲完成，24 位输出数据从最高位至最低位逐位输出完成。第 25至 27 个时钟脉冲用来选择下一次 A/D 转换的输入通道和增益

---



## _stabilizer函数

```python
def _stabilizer(values, deviation=10):weights = []
        for prev in values:
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
```

这段代码定义了 `_stabilizer` 函数，其功能是从一组数值 `values` 中，找出“最稳定”的值。稳定性的衡量基于每个值与其他值的偏差关系。以下是对代码的详细解析和功能解释：

---

### **函数的参数**

1. **`values`** :

* 一个可迭代对象，包含多个数值。
* 假设这些数值可能有一些波动，例如传感器的测量值。

1. **`deviation`** :

* 默认为 10，表示允许的偏差百分比。
* 用于判断一个值与其他值是否足够接近。

#### 1. 初始化权重列表

```python
weights = []
for prev in values:
    weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
```

 **作用** ：

* 遍历每个值 `prev`，计算它与其他值 `current` 的偏差。
* 如果两个值的相对偏差（以百分比表示）在 `deviation` 允许范围内，则认为它们是“接近”的。
* 计算有多少个值与当前值 `prev` 接近，并将其作为权重存储在 `weights` 列表中。

 **核心计算逻辑** ：

* 相对偏差：
  偏差百分比=∣prev?current∣/prev×100
* 判断条件：
  如果偏差百分比 ≤deviation，则认为两个值接近。

#### 2. 排序并返回最稳定值

```python
return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
```

 **作用** ：

* 将 `values` 和 `weights` 组合成一个列表：`[(value1, weight1), (value2, weight2), ...]`。
* 按照权重 `weights` 对列表进行排序（权重从小到大）。
* 使用 `pop()` 移除并返回最后一个元素的值（即权重最大的值）。
