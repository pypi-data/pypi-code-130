from gym.envs.registration import register

register(
    id='gymbullet_diffbotenv-v1.1',
    entry_point='gymbullet_diffbotenv.envs:DB_Env',
)