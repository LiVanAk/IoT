## ����ͨѶ

����ͨѶ���ɹܽ� PD_SCK �� DOUT ��ɣ�����������ݣ�ѡ������ͨ�������档����������ܽ� DOUT Ϊ�ߵ�ƽʱ������A/D ת������δ׼����������ݣ���ʱ����ʱ�������ź� PD_SCK ӦΪ�͵�ƽ���� DOUT �Ӹߵ�ƽ��͵�ƽ��PD_SCK Ӧ���� 25 �� 27 �����ȵ�ʱ�����壨ͼ���������е�һ��ʱ������������� ��������� 24 λ���ݵ����λ��MSB����ֱ���� 24 ��ʱ��������ɣ�24 λ������ݴ����λ�����λ��λ�����ɡ��� 25�� 27 ��ʱ����������ѡ����һ�� A/D ת��������ͨ��������

---



## _stabilizer����

```python
def _stabilizer(values, deviation=10):weights = []
        for prev in values:
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
```

��δ��붨���� `_stabilizer` �������书���Ǵ�һ����ֵ `values` �У��ҳ������ȶ�����ֵ���ȶ��Եĺ�������ÿ��ֵ������ֵ��ƫ���ϵ�������ǶԴ������ϸ�����͹��ܽ��ͣ�

---

### **�����Ĳ���**

1. **`values`** :

* һ���ɵ������󣬰��������ֵ��
* ������Щ��ֵ������һЩ���������紫�����Ĳ���ֵ��

1. **`deviation`** :

* Ĭ��Ϊ 10����ʾ�����ƫ��ٷֱȡ�
* �����ж�һ��ֵ������ֵ�Ƿ��㹻�ӽ���

#### 1. ��ʼ��Ȩ���б�

```python
weights = []
for prev in values:
    weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
```

 **����** ��

* ����ÿ��ֵ `prev`��������������ֵ `current` ��ƫ�
* �������ֵ�����ƫ��԰ٷֱȱ�ʾ���� `deviation` ����Χ�ڣ�����Ϊ�����ǡ��ӽ����ġ�
* �����ж��ٸ�ֵ�뵱ǰֵ `prev` �ӽ�����������ΪȨ�ش洢�� `weights` �б��С�

 **���ļ����߼�** ��

* ���ƫ�
  ƫ��ٷֱ�=�Oprev?current�O/prev��100
* �ж�������
  ���ƫ��ٷֱ� ��deviation������Ϊ����ֵ�ӽ���

#### 2. ���򲢷������ȶ�ֵ

```python
return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
```

 **����** ��

* �� `values` �� `weights` ��ϳ�һ���б�`[(value1, weight1), (value2, weight2), ...]`��
* ����Ȩ�� `weights` ���б��������Ȩ�ش�С���󣩡�
* ʹ�� `pop()` �Ƴ����������һ��Ԫ�ص�ֵ����Ȩ������ֵ����
