# Patent Veri Toplama ve API Projesi

Bu proje, veri toplama ve API hizmeti sağlamak amacıyla kullanılan bir Python uygulamasını içerir.

## Başlangıç

Bu projenin amacı, https://patents.justia.com sitesinden patent verilerini çekmek ve bu verileri daha sonra bir API üzerinden kullanılabilir hale getirmektir. Proje üç ana bölümden oluşur: Web Scraping, Vector Embeddings ve API Endpoint for Vector Similarity.

### Kurulum

Bu projeyi çalıştırmak için şunları yapmanız gerekir:

- Bu depoyu kopyalayın: `git clone https://github.com/MrSipahi/patent-semantic-search.git`
- Proje dizinine gidin: `cd patent-semantic-search`
- Gerekli bağımlılıkları yükleyin: `pip install -r requirements.txt`



  
## Servisler

### UrlScraper

```
python main.py urlscraper
```

Bu servis, https://patents.justia.com web sitesinden patent verilerini çekmek için kullanılan bir Python web scraping servisidir. Servis, aşağıdaki görevleri gerçekleştirir:

- Belirli patentlerin web sayfalarını ziyaret eder.
- Sayfalardan patent başlığı, özet ve paragraf bilgilerini çeker.
- Bu verileri bir veritabanına kaydeder ve aynı zamanda bir gömme modeli kullanarak metinleri vektörlere dönüştürür.

Servis aynı zamanda hata yönetimini de içerir. Eğer bir sayfa yüklenemezse veya eksik veri bulunursa, hata işleme mekanizması devreye girer.

### Vector Search API

```
python main.py api
```

Bu API, vektör tabanlı metin araması yapmak için kullanılan bir Flask RESTful servisidir. Bu API, belirli bir metin sorgusunu alır, bu sorguyu bir vektöre dönüştürür, daha sonra bu vektörü bir veritabanındaki diğer vektörlerle karşılaştırarak benzer metinleri döndürür.

#### Endpoint Search

```
  POST /patent/search
```

| Parametre | Tip     | Açıklama        | Default          
| :--------|:-------|:-------------------------|:---------|
| `query` | `string` | **Gerekli**. Arama sorgusu | -
| `model` | `string` | Kullanılacak vektör modeli | pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb
| `limit` | `int` | Döndürülecek sonuç sayısı sınırı | 10
| `collection_name` | `string` | Veritabanı koleksiyon adı. | bio_patent

Body
```
{
    "query": "Ornithine transcarbamylase deficiency",
    "limit":10
}
```
 Example Response
```
{
    "embedding_time": 0.26,
    "search_time": 0.02,
    "result": [
        {
            "id": 445348296624204956,
            "patent_id": 10487133,
            "paragraph": "The use of recombinant proteins as therapeutics to combat ... ",
            "abstract": "The invention provides methods for producing a protein...",
            "score": 176.19
        },
}
```

#### Endpoint Get Parent
```
  GET /patent/<patent_id>
```

| Parametre | Tip     | Açıklama        | Default          
|:-----|:-----|:-------|:----|
| `patent_id` | `int` | **Gerekli**. Getirilecek patentin kimliği. | -


Example Response
```
{
    "id": 445348296624204956,
    "patent_id": 10487133,
    "paragraph": "The use of recombinant proteins as therapeutics to combat disease...",
    "title": " Codon optimization for titer and fidelity improvement ",
    "abstract": "The invention provides methods for producing a protein..."
}
```

### Web Page
HTML dosyasını bir web tarayıcısında açarak sayfanın tasarımını ve işlevselliğini görebilirsiniz. Sayfanın tasarımı Bootstrap kullanılarak oluşturulmuş ve arama sonuçları dinamik olarak gösterilebilir.

Ayrıca, sayfanın içindeki JavaScript kodunu inceleyerek, arama butonuna tıkladığınızda ne tür işlemlerin gerçekleştiğini ve sonuçların nasıl gösterildiğini görebilirsiniz.
