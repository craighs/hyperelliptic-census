{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "v = stats.TimeSeries([1,-4,3,-2.5,-4,3])\n            sage: v[2]\n            3.0\n            sage: v[-1]\n            3.0\n            sage: v[-10]\n            Traceback (most recent call last):\n            ...\n            IndexError: TimeSeries index out of range\n            sage: v[5]\n            3.0\n            sage: v[6]\n            Traceback (most recent call last):\n            ...\n            IndexError: TimeSeries index out of range\n\n        Some slice examples::\n\n            sage: v[-3:]\n            [-2.5000, -4.0000, 3.0000]\n            sage: v[-3:-1]\n            [-2.5000, -4.0000]\n            sage: v[::2]\n            [1.0000, 3.0000, -4.0000]\n            sage: v[3:20]\n            [-2.5000, -4.0000, 3.0000]\n            sage: v[3:2]\n            []\n\n        Make a copy::\n\n            sage: v[:]\n            [1.0000, -4.0000, 3.0000, -2.5000, -4.0000, 3.0000]\n\n        Reverse the time series::\n\n            sage: v[::-1]\n            [3.0000, -4.0000, -2.5000, 3.0000, -4.0000, 1.0000]\n        \");"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    " "
   ]
  }
],
"metadata": {
 "kernelspec": {
  "display_name": "SageMath 10.6",
  "language": "sage",
  "name": "sagemath"
 },
 "language_info": {
  "codemirror_mode": {
   "name": "ipython",
   "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
