{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sage.groups.perm_gps.partn_ref.data_structures import PS_represent\n        sage: PS_represent([[6],[3,4,8,7],[1,9,5],[0,2]], [6,1,8,2])\n        Allocating PartitionStack...\n        Allocation passed:\n        (0 1 2 3 4 5 6 7 8 9)\n        Checking that entries are in order and correct level.\n        Everything seems in order, deallocating.\n        Deallocated.\n        Creating PartitionStack from partition [[6], [3, 4, 8, 7], [1, 9, 5], [0, 2]].\n        PartitionStack's data:\n        entries -> [6, 3, 4, 8, 7, 1, 9, 5, 0, 2]\n        levels -> [0, 10, 10, 10, 0, 10, 10, 0, 10, -1]\n        depth = 0, degree = 10\n        (6|3 4 8 7|1 9 5|0 2)\n        Checking PS_is_discrete:\n        False\n        Checking PS_num_cells:\n        4\n        Checking PS_is_mcr, min cell reps are:\n        [6, 3, 1, 0]\n        Checking PS_is_fixed, fixed elements are:\n        [6]\n        Copying PartitionStack:\n        (6|3 4 8 7|1 9 5|0 2)\n        Checking for consistency.\n        Everything is consistent.\n        Clearing copy:\n        (0 3 4 8 7 1 9 5 6 2)\n        Splitting point 6 from original:\n        0\n        (6|3 4 8 7|1 9 5|0 2)\n        Splitting point 1 from original:\n        5\n        (6|3 4 8 7|1|5 9|0 2)\n        Splitting point 8 from original:\n        1\n        (6|8|3 4 7|1|5 9|0 2)\n        Splitting point 2 from original:\n        8\n        (6|8|3 4 7|1|5 9|2|0)\n        Getting permutation from PS2->PS:\n        [6, 1, 0, 8, 3, 9, 2, 7, 4, 5]\n        Finding first smallest:\n        Minimal element is 5, bitset is:\n        0000010001\n        Finding element 1:\n        Location is: 5\n        Bitset is:\n        0100000000\n        Deallocating PartitionStacks.\n        Done.\n    \");"
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
