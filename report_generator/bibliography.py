import docx
from report_generator.styles import (
    add_chapter_heading, add_body_paragraph
)

def build_bibliography(doc):
    add_chapter_heading(doc, "BIBLIOGRAPHY")

    references = [
        "[1] CatBoost Developer Team. (2023). CatBoost: An open-source gradient boosting on decision trees library. Official Documentation. https://catboost.ai/",
        "[2] HeiGIT gGmbH. (2023). OpenRouteService API Documentation: Directions, Isochrones, and Time-Distance Matrices. Heidelberg Institute for Geoinformation Technology. https://openrouteservice.org/",
        "[3] Meta Platforms, Inc. (2023). React: A JavaScript library for building user interfaces. React Documentation. https://react.dev/",
        "[4] Nie, Y., Nguyen, N. H., Sinthong, P., & Kalagnanam, J. (2023). A Time Series is Worth 64 Words: Long-term Forecasting with Transformers (PatchTST). In Proceedings of the International Conference on Learning Representations (ICLR 2023), Kigali, Rwanda.",
        "[5] OpenStreetMap Contributors. (2024). OpenStreetMap Planet Data and Nominatim Geocoding Service. OpenStreetMap Foundation. https://www.openstreetmap.org/",
        "[6] Pallets Projects. (2023). Flask: A Python Microframework for Web Development. Flask Documentation. https://flask.palletsprojects.com/",
        "[7] Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., ... & Chintala, S. (2019). PyTorch: An Imperative Style, High-Performance Deep Learning Library. In Advances in Neural Information Processing Systems (NeurIPS 2019), 32, 8024-8035.",
        "[8] Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018). CatBoost: Unbiased boosting with categorical features. In Advances in Neural Information Processing Systems (NeurIPS 2018), 31, 6638-6648.",
        "[9] Tailwind Labs. (2023). Tailwind CSS: A utility-first CSS framework for rapid UI development. https://tailwindcss.com/",
        "[10] TomTom International BV. (2024). TomTom Traffic Flow API Documentation: Real-Time Traffic Speeds and Travel Times. https://developer.tomtom.com/",
        "[11] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is All You Need. In Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 5998-6008.",
        "[12] Williams, B. M., & Hoel, L. A. (2003). Modeling and forecasting vehicular traffic flow as a seasonal ARIMA process: Theoretical basis and empirical results. Journal of Transportation Engineering, 129(6), 664-672.",
        "[13] Zhao, L., Song, Y., Zhang, C., Liu, Y., Wang, P., Lin, T., Deng, M., & Li, H. (2019). T-GCN: A Temporal Graph Convolutional Network for Traffic Prediction. IEEE Transactions on Intelligent Transportation Systems, 21(9), 3848-3858.",
        "[14] Zippenfenig, P. (2023). Open-Meteo Weather API: Open-Source Weather API with Global Numerical Weather Prediction Models. https://open-meteo.com/"
    ]

    for ref in references:
        add_body_paragraph(doc, ref)
