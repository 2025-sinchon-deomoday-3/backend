from django.db import migrations


def seed_exchange_universities(apps, schema_editor):
    ExchangeUniversity = apps.get_model("accounts", "ExchangeUniversity")

    data = [
        # 미국
        {"univ_name": "University of California, Davis", "country": "USA", "city": "Davis"},
        {"univ_name": "Rutgers, The State University of New Jersey-New Brunswick", "country": "USA", "city": "New Brunswick"},
        {"univ_name": "University of Massachusetts Amherst", "country": "USA", "city": "Amherst"},
        {"univ_name": "Alma College", "country": "USA", "city": "Alma"},
        {"univ_name": "Georgia State University", "country": "USA", "city": "Atlanta"},
        {"univ_name": "Temple University", "country": "USA", "city": "Philadelphia"},
        {"univ_name": "The George Washington University", "country": "USA", "city": "Washington"},
        {"univ_name": "University of Vermont", "country": "USA", "city": "Burlington"},
        {"univ_name": "Arcadia University", "country": "USA", "city": "Glenside"},
        {"univ_name": "University of Washington", "country": "USA", "city": "Seattle"},
        {"univ_name": "Louisiana State University", "country": "USA", "city": "Baton Rouge"},
        {"univ_name": "San Diego State University", "country": "USA", "city": "San Diego"},
        {"univ_name": "University of Hawaii at Manoa", "country": "USA", "city": "Honolulu"},
        {"univ_name": "Central Washington University", "country": "USA", "city": "Ellensburg"},
        {"univ_name": "American University", "country": "USA", "city": "Washington"},

        # 일본
        {"univ_name": "Rikkyo University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Hosei University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Hitotsubashi University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Tokyo University of Foreign Studies (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Tsuda University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Kwansei Gakuin University (Nishinomiya)", "country": "JAPAN", "city": "Nishinomiya"},
        {"univ_name": "Seisen University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Kansai Gaidai University (Osaka)", "country": "JAPAN", "city": "Osaka"},
        {"univ_name": "Aoyama Gakuin University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Chukyo University (Nagoya)", "country": "JAPAN", "city": "Nagoya"},
        {"univ_name": "Ochanomizu University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Oita University (Oita)", "country": "JAPAN", "city": "Oita"},
        {"univ_name": "Nagoya University (Nagoya)", "country": "JAPAN", "city": "Nagoya"},
        {"univ_name": "Waseda University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Doshisha University (Kyoto)", "country": "JAPAN", "city": "Kyoto"},
        {"univ_name": "Fukuoka University (Fukuoka)", "country": "JAPAN", "city": "Fukuoka"},
        {"univ_name": "Meiji University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Mukogawa Women’s University (Nishinomiya)", "country": "JAPAN", "city": "Nishinomiya"},
        {"univ_name": "Chuo University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Akita International University (Akita)", "country": "JAPAN", "city": "Akita"},
        {"univ_name": "International Christian University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Kyoto Sangyo University (Kyoto)", "country": "JAPAN", "city": "Kyoto"},
        {"univ_name": "St. Andrew’s University (Momoyama Gakuin Univ., Osaka)", "country": "JAPAN", "city": "Osaka"},
        {"univ_name": "Toyo Eiwa University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Gakushuin Women’s College (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Kyushu University (Fukuoka)", "country": "JAPAN", "city": "Fukuoka"},
        {"univ_name": "Nara Women’s University (Nara)", "country": "JAPAN", "city": "Nara"},
        {"univ_name": "Osaka Kyoiku University (Osaka)", "country": "JAPAN", "city": "Osaka"},
        {"univ_name": "Kwassui Women’s University (Nagasaki)", "country": "JAPAN", "city": "Nagasaki"},
        {"univ_name": "Kyoto Women’s University (Kyoto)", "country": "JAPAN", "city": "Kyoto"},
        {"univ_name": "Kobe College (Kobe)", "country": "JAPAN", "city": "Kobe"},
        {"univ_name": "Osaka University of Economics and Law (Osaka)", "country": "JAPAN", "city": "Osaka"},
        {"univ_name": "Sophia University (Tokyo)", "country": "JAPAN", "city": "Tokyo"},
        {"univ_name": "Tokyo University of the Arts (Tokyo)", "country": "JAPAN", "city": "Tokyo"},

        # 독일
        {"univ_name": "Philipps University of Marburg", "country": "GERMANY", "city": "Marburg"},
        {"univ_name": "Johannes Gutenberg University Mainz", "country": "GERMANY", "city": "Mainz"},
        {"univ_name": "RWTH Aachen University", "country": "GERMANY", "city": "Aachen"},
        {"univ_name": "European University Viadrina Frankfurt (Oder)", "country": "GERMANY", "city": "Frankfurt (Oder)"},
        {"univ_name": "Justus Liebig University Giessen", "country": "GERMANY", "city": "Giessen"},
        {"univ_name": "Free University of Berlin", "country": "GERMANY", "city": "Berlin"},
        {"univ_name": "University of Tuebingen", "country": "GERMANY", "city": "Tuebingen"},
        {"univ_name": "Technical University of Darmstadt (TU Darmstadt)", "country": "GERMANY", "city": "Darmstadt"},
        {"univ_name": "Frankfurt University of Applied Sciences", "country": "GERMANY", "city": "Frankfurt"},
        {"univ_name": "Saarland University", "country": "GERMANY", "city": "Saarbruecken"},
        {"univ_name": "University of Flensburg", "country": "GERMANY", "city": "Flensburg"},
        {"univ_name": "Duesseldorf University of Applied Sciences", "country": "GERMANY", "city": "Duesseldorf"},
        {"univ_name": "University of Konstanz", "country": "GERMANY", "city": "Konstanz"},
        {"univ_name": "University of Osnabrueck", "country": "GERMANY", "city": "Osnabrueck"},
        {"univ_name": "University of Rostock", "country": "GERMANY", "city": "Rostock"},

        # 프랑스
        {"univ_name": "Institut National des Langues et Civilisations Orientales (INALCO), Paris", "country": "FRANCE", "city": "Paris"},
        {"univ_name": "Sciences Po Paris (Institut d’Etudes Politiques de Paris)", "country": "FRANCE", "city": "Paris"},
        {"univ_name": "Lille Catholic University (Lille, Paris)", "country": "FRANCE", "city": "Lille"},
        {"univ_name": "University of Paris 1, Pantheon-Sorbonne", "country": "FRANCE", "city": "Paris"},
        {"univ_name": "IESEG School of Management (Lille)", "country": "FRANCE", "city": "Lille"},
        {"univ_name": "University of Versailles Saint-Quentin-en-Yvelines", "country": "FRANCE", "city": "Versailles"},
        {"univ_name": "University of Strasbourg", "country": "FRANCE", "city": "Strasbourg"},
        {"univ_name": "Sciences Po Lyon (Institut d’Etudes Politiques de Lyon)", "country": "FRANCE", "city": "Lyon"},
        {"univ_name": "University of Caen Normandy", "country": "FRANCE", "city": "Caen"},
        {"univ_name": "Gustave Eiffel University (Marne-La-Vallee)", "country": "FRANCE", "city": "Marne-la-Vallee"},
        {"univ_name": "Sciences Po Rennes (Institut d’Etudes Politiques de Rennes)", "country": "FRANCE", "city": "Rennes"},
        {"univ_name": "University of Bordeaux", "country": "FRANCE", "city": "Bordeaux"},
        {"univ_name": "Bordeaux Montaigne University (Pessac)", "country": "FRANCE", "city": "Pessac"},
        {"univ_name": "Sciences Po Saint-Germain-en-Laye", "country": "FRANCE", "city": "Saint-Germain"},
        {"univ_name": "Paris School of Business, Group ESG", "country": "FRANCE", "city": "Paris"},
        {"univ_name": "Emlyon Business School (Ecully)", "country": "FRANCE", "city": "Ecully"},
        {"univ_name": "IPAG Business School (Paris)", "country": "FRANCE", "city": "Paris"},
        {"univ_name": "University of Paris 3, Sorbonne Nouvelle", "country": "FRANCE", "city": "Paris"},

        # 중국
        {"univ_name": "Beijing Institute of Technology", "country": "CHINA", "city": "Beijing"},
        {"univ_name": "Fudan University", "country": "CHINA", "city": "Shanghai"},
        {"univ_name": "Peking University", "country": "CHINA", "city": "Beijing"},
        {"univ_name": "Beijing Normal University", "country": "CHINA", "city": "Beijing"},
        {"univ_name": "Wuhan University", "country": "CHINA", "city": "Wuhan"},
        {"univ_name": "Jinan University", "country": "CHINA", "city": "Guangzhou"},
        {"univ_name": "Renmin University of China", "country": "CHINA", "city": "Beijing"},
        {"univ_name": "Tsinghua University", "country": "CHINA", "city": "Beijing"},
        {"univ_name": "Jilin University", "country": "CHINA", "city": "Changchun"},
        {"univ_name": "Shandong University", "country": "CHINA", "city": "Jinan"},
        {"univ_name": "Shanghai University", "country": "CHINA", "city": "Shanghai"},
        {"univ_name": "The Chinese University of Hong Kong, Shenzhen", "country": "CHINA", "city": "Shenzhen"},

        # 대만
        {"univ_name": "National Taiwan University", "country": "TAIWAN", "city": "Taipei"},
        {"univ_name": "National Chengchi University", "country": "TAIWAN", "city": "Taipei"},
        {"univ_name": "National Taiwan Normal University", "country": "TAIWAN", "city": "Taipei"},
        {"univ_name": "National Yang Ming Chiao Tung University", "country": "TAIWAN", "city": "Hsinchu"},
        {"univ_name": "TamKang University", "country": "TAIWAN", "city": "New Taipei"},
        {"univ_name": "Fu Jen Catholic University", "country": "TAIWAN", "city": "New Taipei"},
        {"univ_name": "National Sun Yat-sen University", "country": "TAIWAN", "city": "Kaohsiung"},
        {"univ_name": "National Cheng Kung University", "country": "TAIWAN", "city": "Tainan"},
        {"univ_name": "National Taipei University of Technology", "country": "TAIWAN", "city": "Taipei"},
        {"univ_name": "National Yang Ming Chiao Tung University (duplicate)", "country": "TAIWAN", "city": "Hsinchu"},

        # 캐나다
        {"univ_name": "University of Waterloo", "country": "CANADA", "city": "Waterloo"},
        {"univ_name": "Wilfrid Laurier University", "country": "CANADA", "city": "Waterloo"},
        {"univ_name": "University of British Columbia", "country": "CANADA", "city": "Vancouver"},
        {"univ_name": "University of Toronto", "country": "CANADA", "city": "Toronto"},
        {"univ_name": "University of Montreal", "country": "CANADA", "city": "Montreal"},
        {"univ_name": "University of Windsor", "country": "CANADA", "city": "Windsor"},
        {"univ_name": "University of the Fraser Valley", "country": "CANADA", "city": "Abbotsford"},
        {"univ_name": "Mount Saint Vincent University", "country": "CANADA", "city": "Halifax"},
        {"univ_name": "York University", "country": "CANADA", "city": "Toronto"},
        {"univ_name": "Mount Allison University", "country": "CANADA", "city": "Sackville"},

        # 이탈리아
        {"univ_name": "Ca’Foscari University of Venice", "country": "ITALY", "city": "Venice"},
        {"univ_name": "University of Bologna", "country": "ITALY", "city": "Bologna"},
        {"univ_name": "Sapienza University of Rome", "country": "ITALY", "city": "Rome"},
        {"univ_name": "University of Turin (Torino)", "country": "ITALY", "city": "Turin"},
        {"univ_name": "Universita Cattolica del Sacro Cuore (Milano)", "country": "ITALY", "city": "Milan"},
        {"univ_name": "University for Foreigners of Siena", "country": "ITALY", "city": "Siena"},
        {"univ_name": "IULM University (Milano)", "country": "ITALY", "city": "Milan"},
        {"univ_name": "Carlo Cattaneo University", "country": "ITALY", "city": "Castellanza"},
        {"univ_name": "Free University of Bozen-Bolzano", "country": "ITALY", "city": "Bolzano"},
        {"univ_name": "University of Pisa", "country": "ITALY", "city": "Pisa"},

        # 네덜란드
        {"univ_name": "Maastricht University", "country": "NETHERLANDS", "city": "Maastricht"},
        {"univ_name": "NHL Stenden University of Applied Sciences (Leeuwarden)", "country": "NETHERLANDS", "city": "Leeuwarden"},
        {"univ_name": "Tilburg University", "country": "NETHERLANDS", "city": "Tilburg"},
        {"univ_name": "Amsterdam University of Applied Sciences", "country": "NETHERLANDS", "city": "Amsterdam"},
        {"univ_name": "Fontys University of Applied Sciences (Eindhoven)", "country": "NETHERLANDS", "city": "Eindhoven"},
        {"univ_name": "University of Groningen", "country": "NETHERLANDS", "city": "Groningen"},
        {"univ_name": "Leiden University", "country": "NETHERLANDS", "city": "Leiden"},

        # 영국
        {"univ_name": "University of Exeter", "country": "UK", "city": "Exeter"},
        {"univ_name": "University of Lancashire", "country": "UK", "city": "Preston"},
        {"univ_name": "York St John University", "country": "UK", "city": "York"},
        {"univ_name": "King’s College London", "country": "UK", "city": "London"},
        {"univ_name": "University of Birmingham", "country": "UK", "city": "Birmingham"},
        {"univ_name": "SOAS, University of London", "country": "UK", "city": "London"},
        {"univ_name": "Lancaster University", "country": "UK", "city": "Lancaster"},
        {"univ_name": "University of Bradford", "country": "UK", "city": "Bradford"},
        {"univ_name": "The University of Manchester", "country": "UK", "city": "Manchester"},
        {"univ_name": "University of Sussex", "country": "UK", "city": "Brighton"},
        {"univ_name": "University of York", "country": "UK", "city": "York"},
        {"univ_name": "University of Chester", "country": "UK", "city": "Chester"},
        {"univ_name": "Nottingham Trent University", "country": "UK", "city": "Nottingham"},
        {"univ_name": "University of Essex", "country": "UK", "city": "Colchester"},
        {"univ_name": "Kingston University", "country": "UK", "city": "Kingston upon Thames"},
        {"univ_name": "University of Bristol", "country": "UK", "city": "Bristol"},
        {"univ_name": "University of the Arts London", "country": "UK", "city": "London"},
    ]

    for item in data:
        ExchangeUniversity.objects.get_or_create(
            univ_name=item["univ_name"],
            defaults={
                "country": item["country"],
                "city": item["city"],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_exchange_universities),
    ]
