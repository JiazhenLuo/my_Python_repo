fetch('dbmovieList2025.json')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('poster-container');

    const postersByMonth = {};

    data.forEach(movie => {
        if (
            !movie['打分日期'] || 
            !movie['封面'] || 
            movie['封面'].includes('movie_default_small.png')
          ) return;
      const month = new Date(movie['打分日期']).getMonth() + 1;
      if (!postersByMonth[month]) postersByMonth[month] = [];
      postersByMonth[month].push({
        date: new Date(movie['打分日期']),
        poster: movie['封面']
      });
    });

    const monthNames = ['Janurary','February','March','April','May','June','July','Auguest','September','Octover','November','December'];

    Object.keys(postersByMonth).sort((a,b) => a - b).forEach(month => {
      const block = document.createElement('div');
      block.className = 'month-block';

      const title = document.createElement('div');
      title.className = 'month-title';
      title.textContent = monthNames[month - 1];

      const grid = document.createElement('div');
      grid.className = 'grid';

      postersByMonth[month]
        .sort((a, b) => a.date - b.date)
        .forEach(item => {
          const img = document.createElement('img');
          img.src = `https://images.weserv.nl/?url=${item.poster.replace(/^https?:\/\//, '')}`;
          grid.appendChild(img);
      });

      block.appendChild(title);
      block.appendChild(grid);
      container.appendChild(block);
    });
  });