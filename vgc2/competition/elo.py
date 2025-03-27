# https://www.geeksforgeeks.org/elo-rating-algorithm/

# Python 3 program for Elo Rating
import math


# Function to calculate the Probability
def probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


# Function to calculate Elo rating
# K is a constant.
# d determines whether
# Player A wins or Player B.
def elo_rating(r_a, r_b, d, k=30):
    # To calculate the Winning
    # Probability of Player A
    p_a = probability(r_a, r_b)

    # To calculate the Winning
    # Probability of Player B
    p_b = probability(r_b, r_a)

    # Case 0 When Player A wins
    # Updating the Elo Ratings
    if d == 0:
        r_a = r_a + k * (1 - p_a)
        r_b = r_b + k * (0 - p_b)

    # Case 1 When Player B wins
    # Updating the Elo Ratings
    else:
        r_a = r_a + k * (0 - p_a)
        r_b = r_b + k * (1 - p_b)

    return r_a, r_b
