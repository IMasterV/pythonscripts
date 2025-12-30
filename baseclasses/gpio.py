import aiofiles

class GPIO:
    def __init__(self):
        self._gpio_in1 = "/sys/class/gpio/GPIO_in1/value"
        self._gpio_in2 = "/sys/class/gpio/GPIO_in2/value"
        self._gpio_out1 = "/sys/class/gpio/GPIO_out1/value"
        self._gpio_out2 = "/sys/class/gpio/GPIO_out2/value"

    @staticmethod
    async def gpio_access(path, mode="r", value=None):
        """
        Универсальная функция для работы с GPIO через sysfs.

        :param path: путь к файлу (например, /sys/class/gpio/GPIO_in1/value)
        :param mode: режим - "r" (чтение) или "w" (запись)
        :param value: строка для записи ("0" или "1"), если mode="w"
        :return: строка со значением при чтении, None при записи
        """

        if mode == "r":
            async with aiofiles.open(path, "r") as file:
                return (await file.read()).strip()

        elif mode == "w":
            if value is None:
                raise ValueError("Для записи нужно указать value")

            async with aiofiles.open(path, "w") as file:
                await file.write(value)
            return None
        else:
            raise ValueError("mode должен быть 'r' или 'w'")

    async def wr_out1(self, value):
        await self.gpio_access(self._gpio_out1, mode="w", value=value)

    async def wr_out2(self, value):
        await self.gpio_access(self._gpio_out2, mode="w", value=value)

    async def rd_in1(self):
        return await self.gpio_access(self._gpio_in1)

    async def rd_in2(self):
        return await self.gpio_access(self._gpio_in2)