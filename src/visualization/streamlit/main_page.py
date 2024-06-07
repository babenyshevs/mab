import os

import streamlit as st

from src.general.io import read_yaml

st.set_page_config(page_title="Main page", page_icon="📊", layout="wide")

dir_path = os.path.dirname(os.path.realpath(__file__))
fig_path = dir_path.replace("src/visualization/streamlit", "reports/figures/streamlit")
if "cfg" not in st.session_state:
    st.session_state["cfg"] = read_yaml(f"{dir_path}/default.yml")

st.title("Comparison of A/B Test and Multi-Armed Bandit (MAB) on Data")
st.markdown(
    """
    # Navigation
    Welcome to the MAB vs. A/B Test Visualization App.
    Use the sidebar to navigate to different pages.
    - Simulation: Adjust reward settings for different arms.
    - Data: Compare the performance of A/B Testing and Multi-Armed Bandit.
    - Algorithm: Learn about different algorithms used in A/B Testing and Multi-Armed Bandit.
    """
)

st.markdown(
    """
     ---
    # Theoretical Framework
    ---
    ## Summary

    - A/B testing is a method to improve products.
    - The right way to do it: test > evaluate > improve > test.
    - There's a danger of false positive results if done incorrectly.
    - There are alternatives with better business impact.

    ---
    ## A/B Tests
    ### 1. What is A/B Testing?
    A/B testing, also known as split testing or case-control study, is a method used to compare two 
    or more versions of a product or service to determine which one performs better. 
    In chatbot development, this means comparing different variations of the chatbot's design, 
    content, or functionality to identify the most effective approach.
    """
)
st.image("./reports/figures/streamlit/ab_test_flow_v2.png", width=500)
with st.expander("example", expanded=False):
    st.write(
        """
        A telecommunication is developing a chatbot to assist customers with troubleshooting 
        internet connection issues. They create two variations of the chatbot: 
        - Version A provides step-by-step instructions for troubleshooting.
        - Version B offers users the option to connect with a live customer support representative.
        
        Users are randomly assigned to one of the variants. A statistical analysis is performed 
        to determine which variation performs better for a defined business goal.
        """
    )
st.markdown(
    """
    #### 1.1 Why to perform it?
    In short - to **optimize business metrics**. With A/B testing, one can make more out of 
    existing traffic as even small changes can lead to better user engagement, increased customer 
    satisfaction, and achieving business objectives more effectively.
    """
)
with st.expander("example", expanded=False):
    st.write(
        """ 
    The telecommunications company analyzes the results of their A/B test and discovers that 
    Version B of the chatbot, which offers users the option to connect with a live support 
    representative, significantly increases user satisfaction and reduces the time to resolve 
    issues compared to Version A. As a result, they decide to implement Version B as 
    the default option for their chatbot.
    """
    )
st.markdown(
    """
    #### 1.2 What are the steps 
    - Define clear objectives: Increase customer satisfaction and reduce resolution time for internet 
    connection issues.
    - Identify variables: Test different approaches for assisting users with troubleshooting.
    - Create variations: Develop Version A with step-by-step instructions and Version B with the option
    to connect with live support.
    - Randomize assignment: Randomly assign users to interact with either Version A or Version B of the 
    chatbot.
    - Collect data: Monitor user interactions and collect data on user satisfaction and issue resolution
    time.
    - Analyze results: Use statistical analysis to compare the performance of Version A and Version B.
    - Implement changes: Based on the analysis, implement the more effective version of the chatbot.
    """
)
st.image("./reports/figures/streamlit/ab_test_process.png", width=500)
st.markdown(
    """
    #### 1.3 A/B vs. Multivariate Testing
    When an object is **modified in more than one way**, we call it Multivariate Testing.
    Multivariate testing allows for simultaneous testing of multiple variables and interactions between 
    them, providing insights into the combined effects of different elements on user behavior.
    """
)
st.image("./reports/figures/streamlit/ab_vs_multivariate.png", width=600)
with st.expander("example", expanded=False):
    st.write(
        """
        The telecom expands A/B testing to include variations in pricing options, promotional messages, 
        and website layout. They use multivariate testing to analyze the combined impact of 
        these variables on sign-up conversions and user engagement.
        """
    )

st.markdown(
    """
    ##### Caution!
    What if we would test many groups, say, 10, and use 5 metrics? Even intuitively, if we will make 
    many attempts to find a difference between groups, finally we would find one with the difference. 
    This phenomenon is also related to [p-hacking](https://en.wikipedia.org/wiki/Data_dredging).
    Danger which it brings is known as **spurious correlations**, which could be **nothing but random 
    fluctuations**, e.g.:
    """
)
with st.expander("example", expanded=False):
    cols1 = st.columns(spec=2, gap="large")
    with cols1[0]:
        st.image("./reports/figures/streamlit/spurious_corr.png", width=500)

    with cols1[1]:
        st.image("./reports/figures/streamlit/spurious_corr2.png", width=500)
    st.markdown(
        """
    See more at [National Geographic](https://www.nationalgeographic.com/science/article/nick-cage-movies-vs-drownings-and-more-strange-but-spurious-correlations).
    """
    )
st.markdown(
    """
    #### 1.4 What are typical metrics?
    | Name                | Type        | Scale    | Business Value |
    |---------------------|-------------|----------|----------------|
    | Rating              | Discrete    | 1-5      | High           |
    | NPS                 | Discrete    | 0 to 10  | High           |
    | Acceptance percent  | Continuous  | 0-1      | High           |
    | Fabricating percent | Continuous  | 0-1      | High           |
    | Incomplete percent  | Continuous  | 0-1      | Low            |
    | ...                 | ...         | ...      | ...            |

    ---
    ### 2. Some statistics behind
    #### 2.1 Why don't just compare means?
    The answer is below. Consider two cases with exactly the same mean values and exactly the same 
    effect size (difference between means).
    """
)
st.image("./reports/figures/streamlit/t_test_dist.png", width=500)
st.markdown(
    """
    Even intuitively, one might say that Case I provides somewhat more certainty of a true 
    difference than Case II. Why? Because of the higher variance of Case II. This is related to 
    the minimum detectable effect.

    #### 2.2 T-test
    Tests whether there is a significant difference between the means of groups. The variable must 
    be normally distributed.
    - Assumptions: The t-test assumes that the data is normally distributed and that the variances 
    of the two groups being compared are equal. It also assumes that the observations are independent.
    - Weaknesses: If the assumptions are violated, the results of the t-test may not be reliable. 
    Additionally, the t-test is sensitive to outliers.
    """
)
st.image("./reports/figures/streamlit/t_test_types.png", width=500)
st.markdown(
    """
    Explaining MDE as well as Type I, II errors, α and β values goes beyond the scope. 
    But perhaps the picture below can give some intuition:
    """
)
st.image("./reports/figures/streamlit/mde.png", width=400)
st.markdown(
    """
    Given all the rest equal, the higher would be the variance of the distributions $H_0$ and $H_1$, 
    the bigger would be the area representing the False Positive rate (Type I error). I.e., we would 
    see the difference between A and B groups, which in fact would be nothing more than a 
    coincidence (see *spurious correlations* examples above).

    #### 2.3 What if assumptions aren't met?
    So far, we considered tests which assume a normal distribution of the variable. 
    Real data rarely meet this assumption. 
    """
)
with st.expander("example", expanded=False):
    st.markdown("""NPS values:""")
    st.image("./reports/figures/streamlit/nps.png", width=500)
st.markdown(
    """
    #### 2.4 How to handle it?
    there are several strategies to deal with it.
    ##### Bootstrap
    In most cases, we may apply the 
    [Central Limit Theorem](https://en.wikipedia.org/wiki/Central_limit_theorem), which states that 
    the distribution of a normalized version of the sample mean converges to a standard normal 
    distribution. This holds even if the original variables themselves are not normally distributed. 
    The method is called [bootstrapping](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)):
    """
)
st.image("./reports/figures/streamlit/bootstrap_method.png", width=500)
st.markdown(
    """
    ##### Wilcoxon rank-sum test (also known as Mann-Whitney U test)

    Determines if there is a difference between two samples. 
    Variables do not have to satisfy any distribution."""
)
st.image("./reports/figures/streamlit/mu_test.png", width=500)
st.markdown(
    """
    ---
    ### 3. A/B Tests drawback and alternatives
    A/B testing is not the only way to test which group is better. Its main advantage is statistical 
    significance. Yet, it comes at the price:
    
    #### 3.1 Resource Intensive
    A/B testing requires a significant amount of resources, especially when dealing with multiple 
    variations and large sample sizes. Each variation needs to be tested independently, leading to 
    increased time and cost.
    """
)
with st.expander("example", expanded=True):
    cols2 = st.columns(spec=2, gap="large")
    with cols2[0]:
        st.image("./reports/figures/streamlit/production_metrics_means.png", width=500)

    with cols2[1]:
        st.image("./reports/figures/streamlit/production_metrics_mde.png", width=500)
    st.markdown(
        """
    These are anonymized production metrics of a Chatbot.
    - Variable 1 reflects desired-behviour metric and is less stable
    - While Variable 2 reflects undesired behaviour and is more stable.
    Both require quite a lot (and still different number) of observations for MDE, say, 2%
    """
    )
st.markdown(
    """
    #### 3.2 Delayed Learning: 
    A/B testing relies on fixed sample sizes and requires data to be collected over a specified period 
    before conclusions can be drawn. This can lead to delays in learning which variation performs better, 
    especially if there are rapid changes in user behavior or if the sample size requirement is not met 
    within a reasonable timeframe.

    #### 3.3 Inflexibility: 
    A/B testing typically requires predefining the variations to be tested before the experiment begins. 
    This can be limiting if new variations or changes need to be introduced during the testing process.

    #### 3.4 External factors: 
    Market trends, seasonal variations, and user demographics may influence the outcome of A/B tests, 
    making it challenging to isolate the impact of specific variables.

    The alternative methods often used, when it comes to production systems with high load and 
    sensitivity to suboptimal solutions, is Reinforcement learning algorithms.
"""
)

###############################################################################
###############################################################################
###############################################################################

st.markdown(
    """
    --- 
    ## Reinforcement Learning
    Reinforcement Learning (RL) is a type of machine learning paradigm where an agent learns to make 
    decisions by interacting with an environment. It is inspired by how humans and animals learn from 
    feedback through trial and error.

    ### 1. Brief introduction
    #### components
    RL systems consist of several key components that interact to enable learning and decision-making.

    """
)
with st.expander("components list", expanded=False):
    st.markdown(
        """
    1. Agent:
    - The entity that learns and makes decisions in the environment.
    - It takes actions based on the current state and the policy.
    2. Environment:
    - The external system with which the agent interacts.
    - It provides feedback to the agent based on its actions.
    3. State:
    - A specific situation or configuration that the agent perceives from the environment.
    - $s \in \mathcal{S}$: set of states.
    4. Action:
    - The decision or choice made by the agent at each time step.
    - Actions affect the state and future rewards.
    - $a \in \mathcal{A}$: set of actions.
    5. Reward:
    - Feedback from the environment to the agent after each action.
    - It quantifies the immediate benefit or desirability of an action.
    - $r \in \mathcal{R}$: set of rewards.
    6. Policy:
    - The strategy or rule that the agent follows to select actions.
    - It maps states to actions and defines the agent's behavior.
    - $P(s'|s,a)$: probability of transitioning to state $s'$ given state $s$ and action $a$.
    - $R(s,a,s')$: reward received after transitioning from state $s$ to state $s'$ by taking action $a$.
    """
    )

st.markdown(
    """
    #### workflow
    The RL process involves a cyclical interaction between the agent and the environment, 
    leading to continuous learning.
    """
)
with st.expander("workflow elements", expanded=False):
    st.markdown(
        """
        1. Initialization:
        - The agent initializes its parameters and the environment.
        2. Interaction:
        - The agent observes the current state from the environment.
        - Based on the state and the policy, the agent selects an action.
        - The action is sent to the environment, which transitions to a new state and provides a reward.
        3. Learning:
        - The agent updates its policy based on the observed reward and transitions.
        - This is often done using techniques like value iteration, Q-learning, or policy gradients.
        4. Iteration:
        - Steps 2 and 3 are repeated iteratively until the agent learns an optimal policy.
        """
    )

st.markdown(
    """
    #### key concepts
    Several fundamental concepts underpin the theory and practice of RL, guiding the agent's learning process.
    """
)
with st.expander("list of concepts", expanded=False):
    st.markdown(
        """
        1. **Exploration vs. Exploitation:**
        - Balancing between trying new actions (exploration) and choosing actions that are known to yield 
        high rewards (exploitation).
        2. **Temporal Credit Assignment:**
        - Determining which actions are responsible for the received rewards, considering delayed 
        consequences.
        3. **Markov Decision Processes (MDPs):**
        - Formal framework used to model RL problems, consisting of states, actions, transition probabilities, 
        and rewards.
        - $$P(s_{t+1}|s_t, a_t, s_{t-1}, a_{t-1}) = P(s_{t+1}|s_t, a_t)$$
        4. **Value Functions:**
        - Functions that estimate the expected cumulative reward of being in a particular state or t
        aking a specific action.
        - $$Q_t(a) = \\frac{\sum_{i=1}^{t-1} R_i \cdot \mathbb{1}_{A_i=a}} {\sum_{i=1}^{t-1} \mathbb{1}_{A_i=a}}$$
        5. **Policy Optimization:**
        - Techniques to improve the agent's policy over time, aiming to maximize long-term rewards.
        """
    )

st.markdown(
    """
    #### solution methods
    Reinforcement Learning (RL) solution methods are techniques used to find the optimal policy for an agent. 
    These methods can be broadly categorized into tabular methods and approximate solution methods.
    
    - Tabular

    Tabular methods are used when the state and action spaces are small enough to be represented 
    explicitly in tabular form. These methods store and update value functions for each state or 
    state-action pair.
        """
)
with st.expander("details", expanded=False):
    st.markdown(
        """
        1. Dynamic Programming (DP)
        - **Description:**
        - Uses a model of the environment to evaluate and improve policies iteratively.
        - Relies on Bellman's equations to update value functions.
        - **Key Algorithms:**
        - Policy Iteration
        - Value Iteration

        2. Monte Carlo Methods
        - **Description:**
        - Learn from episodes of experience without requiring a model of the environment.
        - Estimate value functions based on the average returns received from sampled episodes.
        - **Key Algorithms:**
        - First-Visit Monte Carlo
        - Every-Visit Monte Carlo

        3. Temporal Difference (TD) Learning
        - **Description:**
        - Combines ideas from DP and Monte Carlo methods.
        - Updates value functions based on estimates of future rewards rather than waiting for the end of an episode.
        - **Key Algorithms:**
        - SARSA (State-Action-Reward-State-Action)
        - Q-Learning
        """
    )

st.markdown(
    """
    - Approximate

    Approximate solution methods are used when the state and action spaces are too large to be 
    represented explicitly. These methods approximate the value functions or policies using function
    approximation techniques.
        """
)
with st.expander("details", expanded=False):
    st.markdown(
        """
        1. Function Approximation
        - **Description:**
        - Uses parametric models like linear functions or neural networks to approximate value functions.
        - Enables RL to scale to large or continuous state spaces.
        - **Key Techniques:**
        - Linear Function Approximation
        - Neural Networks

        2. Policy Gradient Methods
        - **Description:**
        - Directly parameterize the policy and optimize it by gradient ascent on expected rewards.
        - Suitable for high-dimensional or continuous action spaces.
        - **Key Algorithms:**
        - REINFORCE
        - Actor-Critic Methods

        3. Deep Reinforcement Learning
        - **Description:**
        - Combines deep learning with RL to handle high-dimensional state and action spaces.
        - Uses deep neural networks to approximate value functions or policies.
        - **Key Algorithms:**
        - Deep Q-Network (DQN)
        - Deep Deterministic Policy Gradient (DDPG)
        - Proximal Policy Optimization (PPO)
        """
    )

###############################################################################
###############################################################################
###############################################################################

st.markdown(
    """
    ## Multi-Armed Bandit in Reinforcement Learning

    The Multi-Armed Bandit (MAB) problem is a foundational concept in reinforcement learning (RL), 
    illustrating core principles of decision-making under uncertainty. It is a simpler setting 
    compared to the full RL framework but shares essential characteristics that are crucial 
    for understanding RL algorithms.

    ### Multi-armed bandit problem
    - The MAB problem is a scenario where an agent faces multiple options (arms) to choose from, 
    each providing a random reward from an unknown probability distribution.
    - The agent's goal is to maximize the total reward over a series of trials by strategically 
    selecting arms.
    """
)
st.image("./reports/figures/streamlit/mab.png", width=800)
st.markdown(
    """
    ### Why to use it business setting?
    Short answer - to test faster, smarter, and more efficient.
    **Give bot second chance** - they are constantly evolving, the best today isn't necessery the best tomorrow and vice  versa
        """
)
st.image("./reports/figures/streamlit/ab_vs_mab.png", width=800)
st.markdown(
    """
**Maximize customer satisfaction** - poor performing bots are cut quickly from the traffic
     """
)
st.image("./reports/figures/streamlit/ab_vs_mab_revenue.png", width=800)
st.markdown(
    """
    ### Key concepts
    arms (action options) and share of the exploration vs. explotation (sometimes also called fit/predict)
    are the main concepts of the MAB algorithm
    """
)
with st.expander("details", expanded=False):
    st.markdown(
        """    
    1. **Arms:**
    - Each arm represents an option or action the agent can take.
    - Pulling an arm results in a reward drawn from a probability distribution specific to that arm.
    2. **Exploration vs. Exploitation:**
    - **Exploration:** Trying different arms to gather information about their reward distributions.
    - **Exploitation:** Selecting the arm believed to offer the highest reward based on current knowledge.
    - The trade-off between exploration and exploitation is a central challenge in MAB problems.
    """
    )
st.markdown(
    """
    ### Learning methods:
    1. **Epsilon-Greedy:**
    - With probability ε, the agent explores a random arm.
    - With probability 1-ε, the agent exploits the best-known arm.
    """
)
st.latex(
    r"""
    A_t = 
    \begin{cases}
    \arg\max_a Q_t(a) & \text{with probability } 1 - \varepsilon \\
    \text{random action} & \text{with probability } \varepsilon
    \end{cases}
    """
)
st.markdown(
    """
    2. **Upper Confidence Bound (UCB):**
    - Selects arms based on an optimistic estimate of their potential rewards, balancing exploration 
    and exploitation.
    """
)
st.latex(
    r"""
    A_t = \text{argmax}_a \left( Q(a) + c \sqrt{\frac{\ln(t)}{N(a)}} \right)
    $$

    $c$: constant controlling the level of exploration
    $N(a)$: number of times action $a$ has been selected
    """
)
st.markdown(
    """
    3. **Thompson Sampling:**
    - Uses Bayesian inference to select arms based on the probability of each arm being optimal.

    4. **Softmax:**
   - Computes the probability of selecting each arm using a softmax function, which gives higher 
   probabilities to arms with higher expected rewards.
    """
)
st.latex(
    r"""
    P(a) = \frac{e^{Q(a) / \tau}}{\sum_{i=1}^{k} e^{Q(i) / \tau}}
    """
)
st.markdown(
    """
    ### Relationship to reinforcement learning
    The Multi-Armed Bandit problem is a critical subfield of reinforcement learning that highlights 
    the fundamental challenge of balancing exploration and exploitation. Understanding MAB problems 
    provides valuable insights and techniques that are directly applicable to more complex RL scenarios. 
    By studying MAB, one gains a foundational understanding of decision-making under uncertainty, 
    which is essential for developing effective RL algorithms.    
    """
)
with st.expander("details", expanded=False):
    st.markdown(
        """    
    #### Simplified Decision-Making:
    - The MAB problem is a simplified version of RL problems where there is no state transition—each decision is independent of previous ones.
    - In RL, the agent must consider how actions influence future states and rewards, adding complexity.

    #### Core Principles:
    - The exploration-exploitation dilemma in MAB is directly applicable to RL, where the agent must decide whether to explore new actions or exploit known rewarding actions.
    - Strategies developed for MAB problems often inspire RL exploration strategies.

    #### Component of RL Algorithms:
    - MAB solutions are often embedded within RL algorithms to handle specific subproblems.
    - For example, during the action selection phase in RL, MAB methods like epsilon-greedy or UCB can be used to decide which action to take.

    #### Learning Without State Transitions:
    - MAB focuses solely on optimizing action selection in a static context without considering state transitions, providing a clear view of the action-reward relationship.
    - This focus helps in developing intuition and techniques for more complex RL scenarios where states and transitions must be considered.
"""
    )
