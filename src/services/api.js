const API_URL = 'http://localhost:5050';

export const fetchWhoopData = async (startDate = null) => {
  try {
    const url = startDate 
      ? `${API_URL}/api/whoop/summary?start_date=${startDate}`
      : `${API_URL}/api/whoop/summary`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching Whoop data:', error);
    throw error;
  }
};

export const sendMessage = async (query, whoopData, conversationHistory) => {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        whoopData,
        conversationHistory
      }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};