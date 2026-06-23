import numpy as np

def two_samples_bootstrap_test(x1: np.ndarray,
                               x2: np.ndarray,
                               n_boot: int = 10_000,
                               random_state: int = 123):
    """
    Bootstrap test for the difference in means between two groups.
    The test is two-sided and the null hypothesis is that the mean of group 1
    is equal to the mean of group 2. (Adapted from Alg. 16.1)

    Returns
    -------
    diff_obs  : float   # observed mean difference (x1 - x2)
    p_value   : float   # two-sided achieved significance level (ASL)
    """
    rng = np.random.default_rng(random_state)
    n_f, n_m = len(x1), len(x2)
    diff_obs = x1.mean() - x2.mean()

    pool = np.concatenate([x1, x2])
    boot_diff = np.empty(n_boot)

    for b in range(n_boot):
        idx = rng.integers(0, len(pool), size=n_f + n_m)
        a_star = pool[idx[:n_f]]
        b_star = pool[idx[n_f:]]
        boot_diff[b] = a_star.mean() - b_star.mean()

    p_value = (np.abs(boot_diff) >= np.abs(diff_obs)).mean()

    return diff_obs, p_value

def grouped_unpaired_bootstrap_test(x1: np.ndarray,
                                    x2: np.ndarray,
                                    groups_1: np.ndarray,
                                    groups_2: np.ndarray,
                                    n_boot: int = 10_000,
                                    random_state: int = 123):
    """
    Bootstrap test for difference in means between two independent group-level samples.
    
    Each input is grouped by its respective group variable.
    Null hypothesis: mean(grouped_x1) == mean(grouped_x2)
    
    Returns
    -------
    d       : float   # observed mean difference
    p-val   : float   # two-sided bootstrap p-value
    ci-95   : tuple   # 95% bootstrap percentile CI for difference
    """
    rng = np.random.default_rng(random_state)
    
    # Compute mean per group
    unique_1 = np.unique(groups_1)
    unique_2 = np.unique(groups_2)
    
    x1_group_means = np.array([x1[groups_1 == g].mean() for g in unique_1])
    x2_group_means = np.array([x2[groups_2 == g].mean() for g in unique_2])
    
    # Observed difference
    T_obs = x1_group_means.mean() - x2_group_means.mean()
    
    # Bootstrap
    T_star = np.empty(n_boot)
    for b in range(n_boot):
        sample_1 = rng.choice(x1_group_means, size=len(x1_group_means), replace=True)
        sample_2 = rng.choice(x2_group_means, size=len(x2_group_means), replace=True)
        T_star[b] = sample_1.mean() - sample_2.mean()
    
    # Two-sided p-value and CI
    p_value = (np.abs(T_star) >= np.abs(T_obs)).mean()
    ci_95 = np.percentile(T_star, [2.5, 97.5])
    
    return {'d': T_obs, 'p-val': p_value, 'ci-95': ci_95}


def grouped_paired_bootstrap_test(x1: np.ndarray,
                                  x2: np.ndarray,
                                  groups_1: np.ndarray,
                                  groups_2: np.ndarray,
                                  n_boot: int=10_000,
                                  random_state: int=123):
    """
    Two-sided bootstrap test for the difference in means between two paired groups.
    The null hypothesis is that x1 == x2 and the alternative is x1 != x2.
    The test uses the absolute mean difference.
    
    Returns
    -------
    d       : float   # observed absolute mean difference.
    p-val   : float   # two-sided bootstrap p-value.
    ci-95   : tuple   # 95% percentile CI for the absolute difference.
    """
    rng = np.random.default_rng(random_state)
    
    # Ensure groups_1 and groups_2 have the same unique elements
    unique_1 = np.sort(np.unique(groups_1))
    unique_2 = np.sort(np.unique(groups_2))
    assert np.array_equal(unique_1, unique_2), "groups_1 and groups_2 must have the same unique elements"
    
    # Compute per-group means for paired samples
    x1_means = np.array([x1[groups_1 == g].mean() for g in unique_1])
    x2_means = np.array([x2[groups_2 == g].mean() for g in unique_2])
    
    # Calculate observed absolute mean difference
    diffs = x1_means - x2_means
    T_obs = diffs.mean()
    
    # Center differences to simulate the null hypothesis (mean difference = 0)
    differences_centered = diffs - diffs.mean()
    n_d = len(differences_centered)
    
    # Bootstrap distribution of the absolute mean difference
    T_star = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.choice(n_d, size=n_d, replace=True)
        T_star[b] = differences_centered[idx].mean()
    
    # Two-sided p-value based on bootstraps
    p_value = (np.abs(T_star) >= np.abs(T_obs)).mean()
    ci_95   = np.percentile(T_star, [2.5, 97.5])
    
    return {'d': T_obs, 'p-val': p_value, 'ci-95': ci_95}


def one_sample_bootstrap_test(x: np.ndarray,
                              mu: float,
                              groups: np.ndarray,
                              n_boot: int=10_000,
                              random_state: int=123):
    """
    
    Bootstrap test for the mean of a group.
    The test is one-sided and the null hypothesis is that the mean of x is greater mu.
    The test assumes x are independent samples if no group or independent across groups if groups are provided.
    (addapted Alg. 16.1)    


    Returns
    -------
    d       : float   # observed grouped mean differenceca.
    p-val   : float   # one-sided achieved significance level (ASL)
    ci-95   : tuple   # 95 % percentile CI for the diff (non-studentised)
    """
    rng = np.random.default_rng(random_state)

    # Compute differences distribution to remove the group dependence and paired samples
    if groups is not None:
        x = np.array([x[groups == g].mean() for g in np.unique(groups)])

    T_obs = x.mean()
    x_h0 = x - (T_obs - mu)
    n_d = len(x_h0)

    # Compute the bootstraped distribution
    T_star = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.choice(n_d, size=n_d, replace=True)
        T_star[b] = x_h0[idx].mean()

    # Compute the statistics
    p_value = (T_star >= T_obs).mean()
    ci_95   = np.percentile(T_star, [2.5, 97.5])

    return {'d': T_obs - mu, 'p-val': p_value, 'ci-95': ci_95}