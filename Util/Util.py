class Util:

    @staticmethod
    def constrain(value: float, min_val: float, max_val: float) -> float:
        """
        Constrain a value to be within the specified range.

        :param value: The value to constrain.
        :param min_val: The minimum value of the range.
        :param max_val: The maximum value of the range.
        :return: The constrained value.
        """
        return max(min(value, max_val), min_val)

